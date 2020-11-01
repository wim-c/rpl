lexer = require 'lexer'
phase1 = require 'phase1'
phase2 = require 'phase2'
phase3 = require 'phase3'

local function has_errors(e)
    if #e == 0 then
        return
    end

    print(('%d errors:'):format(#e))
    for index, err in ipairs(e) do
        print(('%d: line %d, col %d: %s'):format(index, err.line, err.col, err.message))
    end
    return true
end

local function compile(name, org, interpreter, out)
    local f, err = io.open(name, 'r')
    if not f then
        print(err)
        return
    end

    local txt = f:read '*a'
    f:close()

    local lex = lexer.lex(txt)
    local p, e = phase1.compile(lex)
    if has_errors(e) then
        return
    end

    p, e = phase2.transform(p)
    if has_errors(e) then
        return
    end

    local writer = out and phase3.file_writer(out) or phase3.simple_writer
    phase3.emit(p, org, interpreter, writer)
end

return {
    compile = compile,
}
