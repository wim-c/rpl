local instructions = require "instructions"
local operators = require "operators"

-- table of instructions
local ins = instructions.instruction

-- table of operators
local ops = operators.operator

local function branch_count(pc, value)
    -- address offset relative to pc
    local offset = (value & 0xffff) - pc
    if  -0x100 < offset and offset < 0x102 then
        return 2
    end
    return 3
end

local function integer_count(pc, value)
    -- normalize to signed word
    value = operators.normalize(value)
    if value < 0x20 and value >= -0x20 then
        return 1
    elseif value < 0x4000 and value >= -0x4000 then
        return 2
    end
    return branch_count(pc, value)
end

local function ins_count_address(pc, instruction)
    local value = instruction.value.value
    return value and integer_count(pc, value) or 2
end

local function ins_count_bytes(pc, instruction)
    return #instruction.value
end

local function ins_count_constexpr(pc, instruction)
    local value = operators.eval(instruction.value)
    return value and integer_count(pc, value) or 1
end

local function ins_count_dataword(pc, instruction)
    return 2
end

local function ins_count_databyte(pc, instruction)
    return 1
end

local function ins_count_float(pc, instruction)
    return 5
end

local function ins_count_int(pc, instruction)
    return integer_count(pc, instruction.value)
end

local function ins_count_markaddress(pc, instruction)
    local address = instruction.value.value
    instruction.value.value = pc
    return 0, address ~= pc
end

local function op_count_branch(pc, instruction)
    if not instruction.const then
        -- target address is on the argument stack
        return 1
    end
    local value = operators.eval(instruction.const)
    if value then
        return branch_count(pc, value)
    end
    return 2
end

local op_counters = {
    [ops.BEQ] = op_count_branch,
    [ops.BNE] = op_count_branch,
    [ops.CALL] = op_count_branch,
    [ops.GOTO] = op_count_branch,
}

local function ins_count_op(pc, instruction)
    local op_counter = op_counters[instruction.value]
    return op_counter and op_counter(pc, instruction) or 1
end

local function ins_count_string(pc, instruction)
    return #instruction.value + 1
end

local ins_count = {
    [ins.ADDRESS] = ins_count_address,
    [ins.BYTES] = ins_count_bytes,
    [ins.CONSTEXPR] = ins_count_constexpr,
    [ins.DATABYTE] = ins_count_databyte,
    [ins.DATAWORD] = ins_count_dataword,
    [ins.FLOAT] = ins_count_float,
    [ins.INT] = ins_count_int,
    [ins.MARKADDRESS] = ins_count_markaddress,
    [ins.OP] = ins_count_op,
    [ins.STRING] = ins_count_string,
}

local pcode
local function o(offset, current)
    local result = current or pcode
    pcode = result + (offset or 1)
    return result
end

local opcodes = {
    PUSH = o(4, 0xc0 - 1),
    [ops.ADD] = o(),
    [ops.AND] = o(),
    [ops.BEQ] = o(4, pcode - 1),
    [ops.BNE] = o(4, pcode - 1),
    [ops.CALL] = o(4),
    [ops.CHR] = o(),
    [ops.CLR] = o(),
    [ops.DIV] = o(),
    [ops.DROP] = o(),
    [ops.DUP] = o(),
    [ops.EQ] = o(),
    [ops.FETCH] = o(),
    [ops.FN] = o(),
    [ops.FOR] = o(),
    [ops.GE] = o(),
    [ops.GET] = o(),
    [ops.GOTO] = o(4),
    [ops.GT] = o(),
    [ops.INPUT] = o(),
    [ops.INT] = o(),
    [ops.LE] = o(),
    [ops.LT] = o(),
    [ops.MOD] = o(),
    [ops.MUL] = o(),
    [ops.NE] = o(),
    [ops.NEW] = o(),
    [ops.NEXT] = o(),
    [ops.NOT] = o(),
    [ops.OR] = o(),
    [ops.OVER] = o(),
    [ops.PEEK] = o(),
    [ops.PICK] = o(),
    [ops.POKE] = o(),
    [ops.PRINT] = o(),
    [ops.RETURN] = o(),
    [ops.RND] = o(),
    [ops.ROLL] = o(),
    [ops.STOP] = o(),
    [ops.STORE] = o(),
    [ops.STR] = o(),
    [ops.SUB] = o(),
    [ops.SWAP] = o(),
    [ops.SYS] = o(),
}

local function emit(program, org, interpreter, writer)
    -- fixed point computation to determine label addresses.  the number of
    -- bytes per instruction may depend on the specific value of an address or
    -- on constants depending on such an address.  if the number of bytes for
    -- an instruction cannot be determined yet then take the minimum number of
    -- bytes as an estimate.
    repeat
        -- p code starts at offset three from org, after a JSR instruction to
        -- invoke the p code interpreter.
        local pc, rerun = org + 3

        for index, instruction in ipairs(program) do
            local counter = ins_count[instruction.type]
            local bytes, address_changed = counter(pc, instruction)
            rerun = rerun or address_changed
            pc = pc + bytes
        end
    until not rerun

    -- current program counter
    local pc = org

    -- current instruction
    local instruction

    -- helper to write a number of bytes to the provided writer.
    local function write(bytes)
        writer(pc, instruction, bytes)
        pc = pc + #bytes
    end

    local function word(value)
        return (value >> 8) & 0xff, value & 0xff
    end

    local function byte(value)
        return value & 0xff
    end

    local function emit_prolog()
        instruction = {
            type = ins.PROLOG,
            value = interpreter,
        }
        local hi, lo = word(interpreter)
        write {0x20, lo, hi}
    end

    local function emit_relative(base_opcode, value)
        local offset = (value & 0xffff) - pc
        if offset <= 0 and offset > -0x100 then
            -- backward relative branch
            write {base_opcode + 2, byte(-offset)}
        elseif offset >= 2 and offset < 0x102 then
            -- forward relative branch
            write {base_opcode + 3, byte(offset - 2)}
        else
            -- absolute branch
            write {base_opcode + 1, word(value)}
        end
    end

    local function emit_int(value)
        value = operators.normalize(value)
        if value < 0x20 and value >= -0x20 then
            write {(value & 0x3f) | 0x80}
        elseif value < 0x4000 and value >= -0x4000 then
            write {word(value & 0x7fff)}
        else
            emit_relative(opcodes.PUSH, value)
        end
    end

    local function emit_op(value)
        local opcode = opcodes[value]
        if instruction.const then
            emit_relative(opcode, operators.eval(instruction.const))
        else
            write {opcode}
        end
    end

    local function emit_float(value)
        if value == 0 then
            write {0, 0, 0, 0, 0}
        else
            local sign_flag = value < 0 and 0x80000000 or 0
            value = math.abs(value)
            local exp = math.floor(math.log(value, 2))
            local mantissa = math.floor(value*math.pow(2, 31 - exp) + 0.5)
            if mantissa >= 0x100000000 then
                exp = exp + 1
                mantissa = mantissa >> 1
            end
            mantissa = (mantissa & 0x7fffffff) | sign_flag
            local bytes = string.pack('B>I4', exp + 129, mantissa)
            write {string.byte(bytes, 1, -1)}
        end
    end

    local function emit_string(value)
        write {byte(#value), string.byte(value, 1, -1)}
    end

    local function emit_bytes(value)
        write {string.byte(value, 1, -1)}
    end

    local function emit_word(value)
        local hi, lo = word(value)
        write {lo, hi}
    end

    local function emit_byte(value)
        write {byte(value)}
    end

    emit_prolog()
    for _, next_instruction in ipairs(program) do
        instruction = next_instruction
        if next_instruction.type == ins.INT then
            emit_int(next_instruction.value)
        elseif next_instruction.type == ins.CONSTEXPR then
            emit_int(operators.eval(next_instruction.value))
        elseif next_instruction.type == ins.ADDRESS then
            emit_int(next_instruction.value.value)
        elseif next_instruction.type == ins.MARKADDRESS then
            if next_instruction.value.symbol then
                -- no code is generated for a label.  call write just to inform
                -- that the current program counter is labeled.
                write {}
            end
        elseif next_instruction.type == ins.OP then
            emit_op(next_instruction.value)
        elseif next_instruction.type == ins.FLOAT then
            emit_float(next_instruction.value)
        elseif next_instruction.type == ins.STRING then
            emit_string(next_instruction.value)
        elseif next_instruction.type == ins.BYTES then
            emit_bytes(next_instruction.value)
        elseif next_instruction.type == ins.DATAWORD then
            emit_word(operators.eval(next_instruction.value))
        elseif next_instruction.type == ins.DATABYTE then
            emit_byte(operators.eval(next_instruction.value))
        end
    end
    writer(pc)

    return pc
end

local function int_display(value)
    return tostring(operators.normalize(value))
end

local function address_display(value)
    return value.symbol and value.symbol or ('$%04X'):format(value.value)
end

local function constexpr_display(constexpr)
    local parts = {}
    for _, part in ipairs(constexpr) do
        local display
        if part.type == ins.INT then
            display = int_display(part.value)
        elseif part.type == ins.ADDRESS then
            display = address_display(part.value)
        elseif part.type == ins.OP then
            display = part.value
        end
        parts[#parts + 1] = display
    end
    return table.concat(parts, ' ')
end

local function file_writer(out)
    local outfile = io.open(out, 'wb')
    local address = false

    return function(pc, instruction, bytes)
        if not instruction then
            outfile:close()
            return
        elseif not address then
            -- write the address where the program must be loaded as a little
            -- endian word.
            outfile:write(string.char(pc & 0xff, pc >> 8))
            address = true
        end
        outfile:write(string.char(table.unpack(bytes)))
    end
end

local function escape(str)
    return (str:gsub("[^ -\127\160-\255]", function(m)
        return '\\' .. m:byte()
    end))
end

local function simple_writer(pc, instruction, bytes)
    if not instruction then
        return
    elseif instruction.type == ins.MARKADDRESS then
        print(('\n%04X %s:'):format(pc, instruction.value.symbol))
        return
    end

    local value
    if instruction.type == ins.INT then
        value = ('push %s'):format(int_display(instruction.value))
    elseif instruction.type == ins.ADDRESS then
        value = ('push %s'):format(address_display(instruction.value))
    elseif instruction.type == ins.CONSTEXPR then
        value = ('push %s'):format(constexpr_display(instruction.value))
    elseif instruction.type == ins.DATAWORD then
        value = ('word %s'):format(constexpr_display(instruction.value))
    elseif instruction.type == ins.DATABYTE then
        value = ('byte %s'):format(constexpr_display(instruction.value))
    elseif instruction.type == ins.FLOAT then
        value = ('float %f'):format(instruction.value)
    elseif instruction.type == ins.STRING then
        value = ('string "%s"'):format(escape(instruction.value))
    elseif instruction.type == ins.BYTES then
        value = ('bytes \'%s\''):format(escape(instruction.value))
    elseif instruction.type == ins.PROLOG then
        value = ('start interpreter at $%04X'):format(instruction.value)
    elseif instruction.const then
        value = ('%s %s'):format(instruction.value, constexpr_display(instruction.const))
    else
        value = instruction.value
    end

    local bytes_value = {}
    for idx, byte in ipairs(bytes) do
        bytes_value[idx] = ("%02X"):format(byte)
    end
    local bytes_display = table.concat(bytes_value, ' ')
    print(("%04X %-14s %s"):format(pc, bytes_display:sub(1, 14), value))
    for index = 16, #bytes_display, 15 do
        pc = pc + 5
        print(("%04X %-14s"):format(pc, bytes_display:sub(index, index + 13)))
    end
end

return {
    emit = emit,
    simple_writer = simple_writer,
    file_writer = file_writer,
}
