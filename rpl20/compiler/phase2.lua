local instructions = require "instructions"
local operators = require "operators"

-- table of onstruction types
local ins = instructions.instruction

-- table of operators
local ops = operators.operator

local UNHANDLED = 1
local FAIL = 2

local function copy_symbol_value(value)
    if value.type == 'macro' then
        -- macro information is read-only so use the original value
        return value
    end
    -- labels are copied since macros can introduce several labels with the
    -- same name but a different address.
    return {
        type = 'label',
        symbol = value.symbol,
    }
end

-- mark all referenced addresses as used.  this is used to only include
-- implictly created data (for float, string, and bytes literals) that is
-- actually used.  references are marked when the complete program is assembled
-- since some optimization steps might remove address references during
-- assembly of the program.
local function mark_addresses_as_used(program)
    for _, instruction in ipairs(program) do
        if instruction.type == ins.ADDRESS then
            instruction.value.used = true
        elseif instruction.type == ins.CONSTEXPR or 
                instruction.type == ins.DATAWORDS or
                instruction.type == ins.DATABYTES then
            mark_addresses_as_used(instruction.value)
        elseif instruction.type == ins.OP and instruction.const then
            mark_addresses_as_used(instruction.const)
        end
    end
end

local function transform(program_to_optimize)
    local errors = {}

    local function add_error(instruction, msg)
        errors[#errors + 1] = {
            line = instruction.line,
            col = instruction.col,
            message = msg,
        }
        return FAIL
    end

    local function add_error_undefined_symbol(instruction)
        return add_error(instruction, ("undefined symbol '%s'"):format(instruction.value))
    end

    local function add_error_illegal_data_expression(instruction)
        return add_error(instruction, "illegal data expression")
    end

    local symbol_stack = {}
    
    local function push_symbols(s)
        local symbols = {}
        for symbol, value in pairs(s) do
            symbols[symbol] = copy_symbol_value(value)
        end
        symbol_stack[#symbol_stack + 1] = symbols
    end

    local function pop_symbols()
        symbol_stack[#symbol_stack] = nil
    end

    local function find_symbol(symbol_instruction)
        for index = #symbol_stack, 1, -1 do
            local entry = symbol_stack[index][symbol_instruction.value]
            if entry then 
                return entry
            end
        end
    end

    local implicit_programs = {
        [ins.FLOAT] = {},
        [ins.STRING] = {},
        [ins.BYTES] = {},
    }

    local implicit_values = {
        [ins.FLOAT] = {},
        [ins.STRING] = {},
        [ins.BYTES] = {},
    }

    local function create_implicit_data(instruction)
        local values = implicit_values[instruction.type]
        local value = values[instruction.value]
        if not value then
            local implicit_program = implicit_programs[instruction.type]

            value = {
                type = 'label',
                symbol = ('%s.%d'):format(instruction.type, #implicit_program/2 + 1)
            }

            values[instruction.value] = value

            implicit_program[#implicit_program + 1] = instructions.replace(instruction, value, ins.MARKADDRESS)
            implicit_program[#implicit_program + 1] = instruction
        end

        return instructions.replace(instruction, value, ins.ADDRESS)
    end

    local function create_literal_float(value)
        if value == 0 then
            return string.char(0, 0, 0, 0, 0)
        end
        local sign_flag = value < 0 and 0x80000000 or 0
        value = math.abs(value)
        local exp = math.floor(math.log(value, 2))
        local mantissa = math.floor(value*math.pow(2, 31 - exp) + 0.5)
        if mantissa >= 0x100000000 then
            exp = exp + 1
            mantissa = mantissa >> 1
        end
        mantissa = (mantissa & 0x7fffffff) | sign_flag
        return string.pack('B>I4', exp + 129, mantissa)
    end

    local function create_literal_string(value)
        return string.pack('s1', value)
    end

    local function create_literal(instruction)
        if instruction.type == ins.FLOAT then
            return create_literal_float(instruction.value)
        elseif instruction.type == ins.STRING then
            return create_literal_string(instruction.value)
        end
        return instruction.value
    end

    local instruction_stack = {}
    
    local function push_instruction(instruction)
        instruction_stack[#instruction_stack + 1] = instruction
    end

    local function push_instructions(program)
        push_symbols(program.symbols)
        push_instruction {
            type = ins.ENDSCOPE,
        }
        for index = #program, 1, -1 do
            push_instruction(program[index])
        end
    end

    local function push_program(program)
        push_instruction {
            type = ins.EOP,
        }
        push_instructions(program)
    end

    local function push_macro(program)
        push_instructions(program)
    end

    local function pop_instruction()
        local index = #instruction_stack
        local instruction = instruction_stack[index]
        instruction_stack[index] = nil
        return instruction
    end

    -- current parse state
    local state

    -- stack of parse states
    local state_stack = {}

    local function push_state(s)
        state_stack[#state_stack + 1], state = state, s
    end

    local function pop_state(n)
        local index = #state_stack
        state, state_stack[index] = state_stack[index]
        return state
    end

    local function parse_program(source_program, as_data)
        -- program that is being assembled
        local program = {}

        local function add_instruction(instruction)
            operators.push_instruction(program, instruction)
        end

        local function parse_label(instruction)
            local value = find_symbol(instruction)
            instruction = instructions.replace(instruction, value, ins.MARKADDRESS)
            add_instruction(instruction)
        end

        local function parse_symbol(instruction)
            local value = find_symbol(instruction)
            if not value then
                return add_error_undefined_symbol(instruction)
            end
            if value.type == 'macro' then
                push_macro(value.value)
            else
                instruction = instructions.replace(instruction, value, ins.ADDRESS)
                add_instruction(instruction)
            end
        end

        -- helper function to translate the parsed branches of an if
        -- instruction to a flat list of instructions.
        local function add_conditional_branches(instruction, value, alternative)
            -- if tos is a not operator then drop it and switch the value and
            -- alternative programs instead.
            local tos = program[#program]
            if tos and tos.type == ins.OP and tos.value == ops.NOT then
                program[#program] = nil
                value, alternative = alternative or {}, value
            end

            -- translate into a branch-if-false operator to jump over the
            -- conditional part of the if statement.
            local branch = ops.BEQ
            
            -- unless the conditional branch is empty.
            if #value == 0 then
                -- in that case use the alternative branch instead and switch
                -- to a branch-if-true operator.
                branch = ops.BNE
                value, alternative = alternative or {}
            end

            -- if the conditional branch starts with a goto to a const address
            -- then fuse the if statement with that goto.
            local first_instruction = value[1]
            if first_instruction.type == ins.OP and
                    first_instruction.value == ops.GOTO and
                    first_instruction.const then
                -- negate the branch condition
                branch = branch == ops.BEQ and ops.BNE or ops.BEQ

                -- create the branch instruction and add it to the program.
                instruction = instructions.replace(instruction, branch, ins.OP)
                instruction.const = first_instruction.const
                program[#program + 1] = instruction

                -- add the alternative branch (if any)
                if alternative then
                    table.move(alternative, 1, #alternative, #program + 1, program)
                end
                return
            end

            -- if the alternative branch starts with a goto to a const address
            -- then fuse the if statement with that goto.
            first_instruction = alternative and alternative[1]
            if first_instruction and first_instruction.type == ins.OP and
                    first_instruction.value == ops.GOTO and
                    first_instruction.const then
                -- create the branch instruction and add it to the program.
                instruction = instructions.replace(instruction, branch, ins.OP)
                instruction.const = first_instruction.const
                program[#program + 1] = instruction

                -- add the conditional branch
                table.move(value, 1, #value, #program + 1, program)
                return
            end

            -- create an implicit label to branch over the conditional part.
            local label = {
                type = 'label',
            }

            -- setup instructions to mark the target address to branch over the
            -- conditional program and use the address in a branch instruction.
            local mark_instruction = instructions.replace(instruction, label, ins.MARKADDRESS)
            local address_instruction = instructions.replace(instruction, label, ins.ADDRESS)
            local branch_instruction = instructions.replace(instruction, branch, ins.OP)
            add_instruction(address_instruction)
            add_instruction(branch_instruction)

            -- add the conditional program
            table.move(value, 1, #value, #program + 1, program)

            if not alternative then
                -- if there is no alternative program then add the instruction
                -- to mark the branch target to complete the if statement.
                add_instruction(mark_instruction)
                return
            end

            -- if the conditional part does not end with a goto or a return
            -- operator then setup instructions to branch over the alternative
            -- program.
            local mark_end_instruction
            local last_instruction = program[#program]
            if not operators.is_no_return(last_instruction) then
                -- create an implicit label to use as a branch target.
                label = {
                    type = 'label',
                }

                -- create mark, address, and goto instructions to branch over
                -- the alternative program.
                mark_end_instruction = instructions.replace(instruction, label, ins.MARKADDRESS)
                address_instruction = instructions.replace(instruction, label, ins.ADDRESS)
                branch_instruction = instructions.replace(instruction, ops.GOTO, ins.OP)
                add_instruction(address_instruction)
                add_instruction(branch_instruction)
            end

            -- mark the branch target to branch over the conditional program.
            add_instruction(mark_instruction)

            -- add the alternative program
            table.move(alternative, 1, #alternative, #program + 1, program)

            -- mark the branch target to branch over the alternative part (if
            -- needed).
            if mark_end_instruction then
                add_instruction(mark_end_instruction)
            end
        end

        local function parse_if(instruction)
            -- check if both branches are empty
            if #instruction.value == 0 and (not instruction.alternative or #instruction.alternative == 0) then
                -- drop condition and skip if instruction.
                program[#program] = nil
                return
            end

            -- check if the condition (last instruction in the program) is a
            -- constant value.
            local tos = operators.const(program, #program)
            if tos and tos.type == ins.INT then
                -- condition is a constant.  drop the condition and expand the
                -- corresponding branch of the if statement in place.
                program[#program] = nil
                if tos.value ~= 0 then
                    -- condition is always true
                    push_macro(instruction.value)
                elseif instruction.alternative then
                    -- condition is always false
                    push_macro(instruction.alternative)
                end
                return
            end

            -- parse both branches
            local parsed_value, parsed_alternative
            local function state_if(_, conditional_program)
                -- set appropriate branch to parse conditional program
                if parsed_value then
                    parsed_alternative = conditional_program
                else
                    parsed_value = conditional_program
                end
                if instruction.alternative and not parsed_alternative then
                    -- continue to parse alternative branch
                    parse_program(instruction.alternative, as_data)
                else
                    -- both branches parsed.  pop the state and add proper
                    -- instructions for these parsed branches.
                    pop_state()
                    add_conditional_branches(instruction, parsed_value, parsed_alternative)
                end
            end

            -- push new parse state and start parsing the conditional branch.
            push_state(state_if)
            parse_program(instruction.value, as_data)
        end

        local function parse_data(instruction, data_type)
            local function state_data(_, data_program)
                -- execute remaining # and ; instructions and check that all
                -- program entries then represent constant data.  then add all
                -- data instructions directly to the program.  translate word
                -- instructions (of type INT, ADDRESS, or CONSTEXPR) to either
                -- a DATABYTE or DATAWORD instruction.  otherwise data words or
                -- bytes would be pushed on the parameter stack.
                for index, data in ipairs(data_program) do
                    if data.type == ins.OP and data.value == ops.DUP and index > 1 then
                        data = data_program[index - 1]
                    elseif data.type == ins.OP and data.value == ops.OVER and index > 2 then
                        data = data_program[index - 2]
                    elseif not instructions.data[data.type] then
                        return add_error_illegal_data_expression(data)
                    end

                    -- convert word values to either an DATAWORD or DATABYTE
                    -- instruction.  create a constexpr to represent its value.
                    if instructions.word[data.type] then
                        data = instructions.replace(data, operators.constexpr(data), data_type)
                    end
                    add_instruction(data)
                end
                pop_state()
            end

            push_state(state_data)
            parse_program(instruction.value, true)
        end

        local function state_program_common(instruction)
            if instruction.type == ins.EOP then
                return UNHANDLED, program
            elseif instruction.type == ins.ENDSCOPE then
                pop_symbols()
            elseif instruction.type == ins.LABEL then
                return parse_label(instruction)
            elseif instruction.type == ins.SYMBOL then
                return parse_symbol(instruction)
            elseif instruction.type == ins.IF then
                return parse_if(instruction)
            elseif instruction.type == ins.DATAWORDS then
                return parse_data(instruction, ins.DATAWORD)
            elseif instruction.type == ins.DATABYTES then
                return parse_data(instruction, ins.DATABYTE)
            else
                add_instruction(instruction)
            end
        end

        local function state_program(instruction)
            if instruction.type == ins.FLOAT or
                    instruction.type == ins.STRING or
                    instruction.type == ins.BYTES then
                -- add inline float, string, and bytes literals to the implicit
                -- data programs and use an address instruction to that data.
                instruction = create_implicit_data(instruction)
                add_instruction(instruction)
            else
                return state_program_common(instruction)
            end
        end

        local function state_program_as_data(instruction)
            if instruction.type == ins.FLOAT or
                    instruction.type == ins.STRING or
                    instruction.type == ins.BYTES then
                -- override behavior for literal instructions (do not create an
                -- implicit address instruction).
                add_instruction(instruction)
            else
                return state_program_common(instruction)
            end
        end

        push_program(source_program)
        push_state(as_data and state_program_as_data or state_program)
    end

    -- add implicit data segements for literal float, string, and bytes
    -- values.
    local function state_implicit_data(_, program)
        -- mark all referenced addresses as used.
        mark_addresses_as_used(program)

        -- add implicit data only if it is used.
        local function add_instructions(additional)
            for index = 1, #additional - 1, 2 do
                -- check if the label of the mark address instruction is used
                -- in the program.
                if additional[index].value.used then
                    -- if so, then add instruction to mark its adress
                    program[#program + 1] = additional[index]

                    -- and add the literal data instruction
                    program[#program + 1] = additional[index + 1]
                end
            end
        end

        -- add implicitly created (and used) literal data for float, string,
        -- and bytes literals.
        add_instructions(implicit_programs[ins.FLOAT])
        add_instructions(implicit_programs[ins.STRING])
        add_instructions(implicit_programs[ins.BYTES])

        return UNHANDLED, program
    end

    push_state(state_implicit_data)
    parse_program(program_to_optimize)

    local transformed_program
    local instruction = pop_instruction()
    while instruction do
        local result
        result, transformed_program = state(instruction)
        while result == UNHANDLED and pop_state() do
            result, transformed_program = state(instruction, transformed_program)
        end
        if result == FAIL then
            break
        end
        instruction = pop_instruction()
        if result == UNHANDLED and instruction then
            add_error(instruction, "syntax error")
            break
        end
    end

    return transformed_program, errors
end

return {
    transform = transform,
}
