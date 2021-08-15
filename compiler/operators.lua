local instructions = require "instructions"

local ins = instructions.instruction

local operator = {
    ADD = '+',
    AND = 'and',
    BEQ = 'beq',
    BNE = 'bne',
    CALL = '&',
    CHR = 'chr',
    CLR = 'clr',
    DIV = '/',
    DROP = '.',
    DUP = '#',
    EQ = '=',
    FETCH = '@',
    FN = 'fn',
    FOR = 'for',
    GE = '>=',
    GET = 'get',
    GOTO = 'goto',
    GT = '>',
    INPUT = 'input',
    INT = 'int',
    LE = '<=',
    LT = '<',
    MOD = '\\',
    MUL = '*',
    NE = '<>',
    NEW = 'new',
    NEXT = 'next',
    NOT = 'not',
    ON = 'on',
    OR = 'or',
    OVER = ';',
    PEEK = 'peek',
    PICK = '^',
    POKE = 'poke',
    PRINT = 'print',
    RETURN = 'return',
    RND = 'rnd',
    ROLL = '$',
    STOP = 'stop',
    STORE = '!',
    STR = 'str',
    SUB = '-',
    SWAP = '%',
    SYS = 'sys',
}

local operator_names = {}
for mnemonic, name in pairs(operator) do
    operator_names[name] = mnemonic
end

local function normalize(value)
    value = value & 0xffff
    return value < 0x8000 and value or value - 0x10000
end

local function eval_op_add(v1, v2)
    return normalize(v1 + v2)
end

local function eval_op_and(v1, v2)
    return normalize(v1 & v2)
end

local function eval_op_div(v1, v2)
    return normalize(v1 // v2)
end

local function eval_op_eq(v1, v2)
    return normalize(v1) == normalize(v2) and -1 or 0
end

local function eval_op_ge(v1, v2)
    return normalize(v1) >= normalize(v2) and -1 or 0
end

local function eval_op_gt(v1, v2)
    return normalize(v1) > normalize(v2) and -1 or 0
end

local function eval_op_le(v1, v2)
    return normalize(v1) <= normalize(v2) and -1 or 0
end

local function eval_op_lt(v1, v2)
    return normalize(v1) < normalize(v2) and -1 or 0
end

local function eval_op_mod(v1, v2)
    return normalize(v1 % normalize(v2))
end

local function eval_op_mul(v1, v2)
    return normalize(v1 * v2)
end

local function eval_op_ne(v1, v2)
    return normalize(v1) ~= normalize(v2) and -1 or 0
end

local function eval_op_or(v1, v2)
    return normalize(v1 | v2)
end

local function eval_op_sub(v1, v2)
    return normalize(v1 - v2)
end

local function eval_op_int(value)
    return normalize(((value & 0xff) << 8 ) | ((value >> 8) & 0xff))
end

local function eval_op_not(value)
    return normalize(~value)
end

local function const(stack, index)
    local instruction = stack[index]

    if not instruction then
        return
    elseif instruction.type == ins.INT or
            instruction.type == ins.ADDRESS or
            instruction.type == ins.CONSTEXPR then
        return instruction
    elseif instruction.type ~= ins.OP then
        return
    elseif instruction.value == operator.DUP then
        return const(stack, index - 1)
    elseif instruction.value == operator.OVER and const(stack, index - 1) then
        return const(stack, index - 2)
    end
end

-- return the word value of an instruction or nil if no value can be
-- determined.
local function instruction_value(instruction)
    if instruction.type == ins.INT then
        return instruction.value
    elseif instruction.type == ins.ADDRESS then
        return instruction.value.value
    end
end

-- return a program that results in the word value of an instruction.
local function constexpr(instruction)
    if instruction.type == ins.CONSTEXPR then
        return { table.unpack(instruction.value) }
    end
    return { instruction }
end

local function apply_unop(stack, instruction, op)
    local index = #stack

    -- get const word instruction for top stack entry
    local tos = const(stack, index)
    if not tos then
        -- top entry is not a const word, just push the instruction to the
        -- stack to apply the operation.
        stack[index + 1] = instruction
        return
    end

    -- get the word value for the top instruction.
    local value = instruction_value(tos)

    if value then
        -- the word value is known so  compute the result of the operation as a
        -- word.
        instruction = instructions.replace(instruction, op(value), ins.INT)
    else
        -- otherwise form a constexpr instruction with a program to compute the
        -- result as the instruction value.

        -- get program for the instruction
        local exp = constexpr(tos)

        -- add the instruction that performs the operation to the programa and
        -- prepare a constexpr instruction.
        exp[#exp + 1] = instruction
        instruction = instructions.replace(instruction, exp, ins.CONSTEXPR)
    end

    -- replace the top stack entry with a single const word instruction.
    stack[index] = instruction
end

-- replace top two stack entries by result of applying the operator from
-- instruction ins to the argument instructions ins1 and ins2.
local function apply_binop(stack, instruction, op)
    local index = #stack

    -- get const word instructions for top two stack entries
    local nos, tos = const(stack, index - 1), const(stack, index)
    if not nos or not tos then
        -- not both entries represent a const word, just push the instruction
        -- to the stack to apply the operation.
        stack[index + 1] = instruction
        return
    end

    -- get the word values for the two instructions.
    local value1, value2 = instruction_value(nos), instruction_value(tos)

    if value1 and value2 then
        -- if both word values are known then compute the result of the
        -- operation as a word.
        instruction = instructions.replace(instruction, op(value1, value2), ins.INT)
    else
        -- otherwise form a constexpr instruction with a program to compute the
        -- result as the instruction value.

        -- get programs for each of the instructions.
        local exp1, exp2 = constexpr(nos), constexpr(tos)

        -- concatenate the program into a single program.
        table.move(exp2, 1, #exp2, #exp1 + 1, exp1)

        -- add the instruction that performs the operation to the programa and
        -- prepare a constexpr instruction.
        exp1[#exp1 + 1] = instruction
        instruction = instructions.replace(instruction, exp1, ins.CONSTEXPR)
    end

    -- replace top two stack entries with a single instruction.
    stack[index - 1], stack[index] = instruction
end

local function op_swap(stack, instruction)
    local index = #stack

    -- get const word instructions for NOS and TOS.
    local nos, tos = const(stack, index - 1), const(stack, index)
    if not nos or not tos then
        -- not both top stack entries are constant words.  just push the swap
        -- operation.
        stack[index + 1] = instruction
        return
    end

    -- adjust entries to an operator if possible
    if nos == tos then
        nos = instructions.replace(nos, operator.DUP, ins.OP)
    elseif nos == const(stack, index - 2) then
        nos = instructions.replace(nos, operator.OVER, ins.OP)
    end

    if tos == const(stack, index - 3) then
        tos = instructions.replace(tos, operator.OVER, ins.OP)
    elseif tos == const(stack, index - 2) then
        tos = instructions.replace(tos, operator.DUP, ins.OP)
    end

    -- swap NOS and TOS
    stack[index - 1], stack[index] = tos, nos
end

local function op_roll(stack, instruction)
    local index = #stack
    local tos = const(stack, index)
    if not tos or tos.type ~= ins.INT then
        -- top of stack is not a fixed word value.  push the instruction.
        stack[index + 1] = instruction
        return
    elseif tos.value <= 1 then
        -- $ simply drops the top of stack.
        stack[index] = nil
        return
    elseif tos.value == 2 then
        -- 2 $ is the same as % (swap).  drop the top of stack and apply a %
        -- instruction instead.
        stack[index] = nil
        instruction = instructions.replace(instruction, operator.SWAP)
        return op_swap(stack, instruction)
    end

    -- check if all stack entries to rotate represent const words.
    local first_index = index - tos.value
    for pos = first_index, index - 1 do
        if not const(stack, pos) then
            -- non const word found.  push the rotate operation.
            stack[index + 1] = instruction
            return
        end
    end

    -- drop the top of stack (the rotate argument)
    stack[index] = nil

    -- rotate the stack entries.  handle the first two entries to move down
    -- specially since these may be replacable by an operator.
    local first, second, third = const(stack, first_index),
        const(stack, first_index + 1),
        const(stack, first_index + 2)

    -- determined instruction for second stack postion to move down.
    if third == second then
        third = instructions.replace(third, operator.DUP, ins.OP)
    elseif third == const(stack, first_index - 1) then
        third = instructions.replace(third, operator.OVER, ins.OP)
    end

    -- determine instruction for first stack postion to move down.
    if second == const(stack, first_index - 2) then
        second = instructions.replace(second, operator.OVER, ins.OP)
    elseif second == const(stack, first_index - 1) then
        second = instructions.replace(second, operator.DUP, ins.OP)
    end

    -- move first two instructions in place
    stack[first_index], stack[first_index + 1] = second, third

    -- then move the rest of the stack down
    table.move(stack, first_index + 3, index - 1, first_index + 2)

    -- and set the new TOS.  check if the const word can be replaced by an
    -- operator instead.
    if first == const(stack, index - 3) then
        first = instructions.replace(first, operator.OVER, ins.OP)
    elseif first == consts(stack, index - 2) then
        first = instructions.replace(first, operator.DUP, ins.OP)
    end
    stack[index - 1] = first
end

local function op_pick(stack, instruction)
    local index = #stack
    local tos = const(stack, index)
    if not tos or tos.type ~= ins.INT then
        -- top of stack is not a fixed word value.  push the instruction.
        stack[index + 1] = instruction
        return
    elseif tos.value <= 0 then
        -- no effect
        return
    end

    -- check if all stack entries from tos down to the requested index are
    -- const word instructions.
    local first_index = index - tos.value
    for pos = first_index, index - 1 do
        if not const(stack, pos) then
            -- non const word found.  push the get operation.
            stack[index + 1] = instruction
            return
        end
    end

    -- replace argument at tos with instruction at the specified offset in the
    -- stack.
    local first = const(stack, first_index)
    if first == const(stack, index - 2) then
        first = instructions.replace(first, operator.OVER, ins.OP)
    elseif first == const(stack, index - 1) then
        first = instructions.replace(first, operator.DUP, ins.OP)
    end
    stack[index] = first
end

local function op_mul(stack, instruction)
    apply_binop(stack, instruction, eval_op_mul)
end

local function op_sub(stack, instruction)
    apply_binop(stack, instruction, eval_op_sub)
end

local function op_add(stack, instruction)
    apply_binop(stack, instruction, eval_op_add)
end

local function op_eq(stack, instruction)
    apply_binop(stack, instruction, eval_op_eq)
end

local function op_mod(stack, instruction)
    apply_binop(stack, instruction, eval_op_mod)
end

local function op_lt(stack, instruction)
    apply_binop(stack, instruction, eval_op_lt)
end

local function op_le(stack, instruction)
    apply_binop(stack, instruction, eval_op_le)
end

local function op_ne(stack, instruction)
    apply_binop(stack, instruction, eval_op_ne)
end

local function op_gt(stack, instruction)
    apply_binop(stack, instruction, eval_op_gt)
end

local function op_ge(stack, instruction)
    apply_binop(stack, instruction, eval_op_ge)
end

local function op_drop(stack, instruction)
    local index = #stack
    if const(stack, index) then
        stack[index] = nil
    else
        stack[index + 1] = instruction
    end
end

local function op_div(stack, instruction)
    apply_binop(stack, instruction, eval_op_div)
end

local function op_and(stack, instruction)
    apply_binop(stack, instruction, eval_op_and)
end

local function op_int(stack, instruction)
    apply_unop(stack, instruction, eval_op_int)
end

local function op_not(stack, instruction)
    -- check if tos ia also a not operator
    local tos = stack[#stack]
    if tos and tos.type == ins.OP and tos.value == operator.NOT then
        -- if so then it is canceled by this second not.  drop tos.
        stack[#stack] = nil
        return
    end
    apply_unop(stack, instruction, eval_op_not)
end

local function op_or(stack, instruction)
    apply_binop(stack, instruction, eval_op_or)
end

local function op_branch_always(stack, instruction)
    local index = #stack
    local tos = const(stack, index)
    if not tos then
        stack[index + 1] = instruction
    else
        -- bind the constant address to the operator.
        instruction = instructions.replace(instruction)
        instruction.const = constexpr(tos)

        -- replace tos by the bound goto.
        stack[index] = instruction
    end
end

local op_goto = op_branch_always
local op_call = op_branch_always

local function op_branch(stack, instruction, condition)
    local index = #stack
    local nos, tos = const(stack, index - 1), const(stack, index)
    local value = nos and instruction_value(nos)
    if not tos then
        -- target address is not const.  push the branch instruction.
        stack[index + 1] = instruction
    elseif not value then
        -- condition is not const.  bind the constant address to the branch
        -- operator.
        instruction = instructions.replace(instruction)
        instruction.const = constexpr(tos)

        -- replace tos by the bound branch.
        stack[index] = instruction
    elseif (value ~= 0) ~= condition then
        -- branch is never taken.  drop nos and tos entries and skip the
        -- branch instruction
        stack[index - 1], stack[index] = nil
    else
        -- branch is always taken.  drop nos and tos and push a goto
        -- instruction.
        instruction = instructions.replace(instruction, operator.GOTO)
        instruction.const = constexpr(tos)
        stack[index - 1], stack[index] = instruction
    end
end

local function op_beq(stack, instruction)
    -- condition equal to zero means it represents false.
    return op_branch(stack, instruction, false)
end

local function op_bne(stack, instruction)
    -- condition not equal to zero means it represents true.
    return op_branch(stack, instruction, true)
end

local compile_time_ops = {
    [operator.ADD] = op_add,
    [operator.AND] = op_and,
    [operator.BEQ] = op_beq,
    [operator.BNE] = op_bne,
    [operator.CALL] = op_call,
    [operator.DIV] = op_div,
    [operator.DROP] = op_drop,
    [operator.EQ] = op_eq,
    [operator.GE] = op_ge,
    [operator.GOTO] = op_goto,
    [operator.GT] = op_gt,
    [operator.INT] = op_int,
    [operator.LE] = op_le,
    [operator.LT] = op_lt,
    [operator.MOD] = op_mod,
    [operator.MUL] = op_mul,
    [operator.NE] = op_ne,
    [operator.NOT] = op_not,
    [operator.OR] = op_or,
    [operator.PICK] = op_pick,
    [operator.ROLL] = op_roll,
    [operator.SUB] = op_sub,
    [operator.SWAP] = op_swap,
}

local eval_binop = {
    [operator.ADD] = eval_op_add,
    [operator.AND] = eval_op_and,
    [operator.DIV] = eval_op_div,
    [operator.EQ] = eval_op_eq,
    [operator.GE] = eval_op_ge,
    [operator.GT] = eval_op_gt,
    [operator.LE] = eval_op_le,
    [operator.LT] = eval_op_lt,
    [operator.MOD] = eval_op_mod,
    [operator.MUL] = eval_op_mul,
    [operator.NE] = eval_op_ne,
    [operator.OR] = eval_op_or,
    [operator.SUB] = eval_op_sub,
}

local eval_unop = {
    [operator.INT] = eval_op_int,
    [operator.NOT] = eval_op_not,
}

local function eval(expr)
    local stack = {}
    local tos = 0
    for _, entry in ipairs(expr) do
        local value = instruction_value(entry)
        if value then
            tos = tos + 1
            stack[tos] = value
        elseif entry.type ~= ins.OP then
            return
        elseif eval_unop[entry.value] then
            stack[tos] = eval_unop[entry.value](stack[tos])
        else
            stack[tos - 1], stack[tos] = eval_binop[entry.value](stack[tos - 1], stack[tos])
            tos = tos - 1
        end
    end
    return stack[1]
end

local function push_instruction(stack, instruction)
    -- check if the instruction is an operator that can be handled inline.  the
    -- case that the operator is already bound to a const value is not handled
    -- inline.
    local op = instruction.type == ins.OP and not instruction.const and compile_time_ops[instruction.value]
    if op then
        op(stack, instruction)
    else
        stack[#stack + 1] = instruction
    end
end

local function is_no_return(instruction)
    return instruction.type == ins.OP and
        (instruction.value == operator.GOTO or
         instruction.value == operator.RETURN or
         instruction.value == operator.STOP)
end

return {
    const = const,
    constexpr = constexpr,
    push_instruction = push_instruction,
    operator = operator,
    operator_names = operator_names,
    eval = eval,
    normalize = normalize,
    is_no_return = is_no_return,
}
