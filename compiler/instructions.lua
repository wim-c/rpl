
local instruction = {
    ADDRESS = 'address',
    BYTES = 'bytes',
    CONSTEXPR = 'constexpr',
    DATABYTE = 'databyte',
    DATABYTES = 'databytes',
    DATAWORD = 'dataword', 
    DATAWORDS = 'datawords', 
    ENDSCOPE = 'endscope',
    EOP = 'eop',
    FLOAT = 'float',
    IF = 'if',
    INT = 'int',
    LABEL = 'label',
    MARKADDRESS = 'markaddress',
    OP = 'op',
    PROLOG = 'prolog',
    STRING = 'string',
    SYMBOL = 'symbol',
}

local function replace(ins, value, type)
    return {
        type = type or ins.type,
        line = ins.line,
        col = ins.col,
        value = value or ins.value,
    }
end

local data = {
    [instruction.ADDRESS] = true,
    [instruction.BYTES] = true,
    [instruction.CONSTEXPR] = true,
    [instruction.FLOAT] = true,
    [instruction.INT] = true,
    [instruction.STRING] = true,
}

local word = {
    [instruction.ADDRESS] = true,
    [instruction.CONSTEXPR] = true,
    [instruction.INT] = true,
}

return {
    instruction = instruction,
    replace = replace,
    data = data,
    word = word,
}
