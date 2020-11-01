local lexer = require "lexer"
local instructions = require "instructions"
local operators = require "operators"

-- dictionary of token names.
local tok = lexer.token

-- table of onstruction types
local ins = instructions.instruction

-- table of operator names
local ops = operators.operator_names

-- tokens that directly translate to an instruction
local tok2ins = {
    [tok.INT] = ins.INT,
    [tok.FLOAT] = ins.FLOAT,
    [tok.STRING] = ins.STRING,
    [tok.BYTES] = ins.BYTES,
    [tok.OP] = ins.OP,
}

-- other reserved keywords
local keywords = {
    ['then'] = true,
    ['end'] = true,
}

-- token not handled in current state.  pop a state from the stack and try
-- again.
local UNHANDLED = 1

-- stop parsing due to unrecoverable error
local FAIL = 2


-- compile phase 1: compile a list of tokens into a program with instructions.
-- no optimizations or macro expansions happen in this phase.
local function compile(tokens)
    -- current compilation state
    local state

    -- stack of pushed compilation states
    local state_stack = {}

    -- push current state and replace it by provided new state
    local function push_state(s)
        state_stack[#state_stack + 1], state = state, s
    end

    -- pop a state from the state stack and make it the current state.  returns
    -- the new current state.
    local function pop_state()
        local stack_len = #state_stack
        state, state_stack[stack_len] = state_stack[stack_len]
        return state
    end

    -- list of errors that are encountered during parsing
    local errors = {}

    -- the current token
    local token

    -- add and error
    local function add_error(msg, line, col)
        errors[#errors + 1] = {
            line = line or token.line,
            col = col or token.col,
            message = msg or "syntax error",
        }
        return FAIL
    end

    local function add_error_missing_end()
        return add_error("missing 'end'")
    end

    local function add_error_missing_delimiter()
        return add_error("missing ']' or ')'")
    end

    local function add_error_missing_label()
        return add_error("missing label before ':'")
    end

    local function add_error_redefined_symbol(prior, label)
        local msg = ("symbol '%s' already defined at line %d col %d"):format(label.value, prior.line, prior.col)
        return add_error(msg, label.line, label.col)
    end

    -- initial parse state
    local function parse_expression()
        -- the program (a list of instructions) being assembled.
        local program = {
            symbols = {},
        }

        -- add an instruction to the program
        local function add_instruction(instruction)
            instruction.line = token.line
            instruction.col = token.col
            program[#program + 1] = instruction
        end

        -- define a symbol in the program's symbol table.  add an error if the
        -- symbol already has a definition in this program.
        local function add_symbol(label, definition)
            definition.symbol = label.value
            local entry = program.symbols[label.value]
            if entry then
                add_error_redefined_symbol(entry, label)
            else
                program.symbols[label.value] = definition
            end
        end

        local function add_label(label)
            add_symbol(label, { type = 'label' })
        end

        local function add_macro(label, program)
            add_symbol(label, {
                    type = 'macro',
                    value = program,
                })
        end

        local function parse_data_or_macro()
            local function state_data_or_macro(data_program)
                if token.type ~= tok.DELIMITER or token.value ~= ']' then
                    return add_error_missing_delimiter()
                end
                if data_program[1] and data_program[1].type == ins.LABEL then
                    local label = table.remove(data_program, 1)
                    add_macro(label, data_program)
                else
                    add_instruction {
                        type = ins.DATAWORDS,
                        value = data_program,
                    }
                end
                pop_state()
            end

            push_state(state_data_or_macro)
            parse_expression()
        end

        local function parse_bytes()
            local function state_bytes(byte_program)
                if token.type ~= tok.DELIMITER or token.value ~= ')' then
                    return add_error_missing_delimiter()
                end
                add_instruction {
                    type = ins.DATABYTES,
                    value = byte_program,
                }
                pop_state()
            end

            push_state(state_bytes)
            parse_expression()
        end

        local function parse_delimiter()
            if token.value == '[' then
                return parse_data_or_macro()
            elseif token.value == '(' then
                return parse_bytes()
            elseif token.value ~= ':' then
                return UNHANDLED, program
            end
            local last_instruction = program[#program]
            if not last_instruction or last_instruction.type ~= ins.SYMBOL then
                return add_error_missing_label()
            end
            last_instruction.type = ins.LABEL
            add_label(last_instruction)
        end

        local function parse_if()
            local instruction = {
                type = ins.IF,
            }
            local function state_if(conditional_program)
                if not instruction.value then
                    instruction.value = conditional_program
                else
                    instruction.alternative = conditional_program
                end
                if token.type ~= tok.IDENT then
                    return add_error_missing_end()
                elseif token.value == 'end' then
                    add_instruction(instruction)
                    pop_state()
                elseif token.value == 'then' and not instruction.alternative then
                    parse_expression()
                else
                   return add_error_missing_end()
                end
            end

            push_state(state_if)
            parse_expression()
        end

        local function parse_ident()
            if token.value == 'if' then
                parse_if()
            elseif ops[token.value] then
                add_instruction {
                    type = ins.OP,
                    value = token.value,
                }
            elseif not keywords[token.value] then
                add_instruction {
                    type = ins.SYMBOL,
                    value = token.value,
                }
            else
                return UNHANDLED, program
            end
        end

        local function state_expression()
            if tok2ins[token.type] then
                -- ? is a shorthand for print but not an official operator
                -- name.
                add_instruction {
                    type = tok2ins[token.type],
                    value = token.value == '?' and 'print' or token.value,
                }
            elseif token.type == tok.DELIMITER then
                return parse_delimiter()
            elseif token.type == tok.IDENT then
                return parse_ident()
            else
                return UNHANDLED, program
            end
        end

        push_state(state_expression)
    end

    -- set initial state to parse an expression.
    parse_expression()

    -- the top level assembled program
    local program

    -- main compilation loop
    for _, t in ipairs(tokens) do
        -- set the current token
        token = t

        -- process token in current state
        local res
        res, program = state()

        -- while the token is unhandled try to pop a state from the stack and
        -- process the token again.
        while res == UNHANDLED and pop_state() do
            res, program = state(program)
        end
        if res == FAIL then
            -- error while processing the current token
            break
        elseif res == UNHANDLED and token.type ~= tok.EOS then
            -- tokens remain while there is no parse state set.
            add_error()
            break
        end
    end

    return program, errors
end

return {
    compile = compile,
}
