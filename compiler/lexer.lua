
local token = {
    STRING = 'string',
    BYTES = 'bytes',
    DELIMITER = 'delimiter',
    IDENT = 'ident',
    INT = 'int',
    FLOAT = 'float',
    OP = 'op',
    EOS = 'eos',
}

local function lex(txt)
    -- position of next character to scan and start of last token
    local pos, start = 1

    -- to keep track of line, col indicators
    local line, base = 1, 0
    
    -- list of scanned tokens
    local tokens = {}

    -- list of lexical errors
    local errors = {}

    -- if not nil then this indicates the position of the last lexical error
    -- that was encountered.
    local last_error

    -- return substring of last match
    local function match(from, to)
        from = from and start + from - 1 or start
        to = to and pos + to or pos - 1
        return string.sub(txt, from, to)
    end

    -- report and error.  does nothing if an error is already pending.  in that
    -- case the error will be added when a new token or the end of txt is
    -- encountered, whichever comes first.
    local function report_error()
        last_error = last_error or {
            start = start,
            line = line,
            col = start - base,
        }
    end

    -- report a pending error.  creates a diagnostic message, adds the error to
    -- the list of errors and then clears the last_error.
    local function add_last_error()
        local last_error_start = last_error.start
        local run = start - last_error_start
        local chars = run < 14 and
            txt:sub(last_error_start, last_error_start + run - 1) or
            txt:sub(last_error_start, last_error_start + 9) .. '...'

        last_error.message = ("skipped %d characters: %q"):format(run, chars)
        errors[#errors + 1], last_error = last_error
    end

    -- add a token to the list of scanned tokens.  if no value is provided then
    -- the match from start to the current position in txt is used as value.
    local function add_token(token, value)
        if last_error then
            -- report and reset last error
            add_last_error()
        end
        tokens[#tokens + 1] = {
            type = token,
            line = line,
            col = start - base,
            value = value or match(),
        }
    end

    -- locate next non-scpae character in txt while keeping track of line count
    -- and last newline position.
    local function peek()
        local from, _, char = string.find(txt, '([\n%S])', pos)
        if char == '\n' then
            line, base, pos = line + 1, from, from + 1
            return peek()
        elseif char then
            start, pos = from, from
            return true
        end
        -- end of input is reached.  set start of next token one past the last
        -- scanned non-space character.
        start = pos
    end

    -- scan for a pattern at the current position in txt.  adjuest position to
    -- just after the matched pattern if found.  returns true if the pattern is
    -- found.
    local function scan(pat)
        local _, to = string.find(txt, pat, pos)
        if to then
            pos = to + 1
            return true
        end
    end

    -- possible multi-byte comparison operators
    local function scan_compare()
        local _, to, op = string.find(txt, '^([<>][>=]?)', pos)
        if op then
            -- a match '>>' counts only as a single '>'.
            pos = op == '>>' and to or to + 1
            return true
        end
    end

    -- scan for a floating point exponent suffix
    local function scan_exponent()
        return scan('^[eE][%-+]?%d+')
    end

    -- main token scanner loop
    while peek() do
        if scan('^%-%-[^\n]*') then
            -- ignore comments
        elseif scan('^"[^\n"]*"') then
            add_token(token.STRING, match(2, -2))
        elseif scan("^'[^\n']*'") then
            add_token(token.BYTES, match(2, -2))
        elseif scan('^[%[%]():]') then
            add_token(token.DELIMITER)
        elseif scan('^@?[_%a][_%w]*') then
            add_token(token.IDENT)
        elseif scan('^%$%x+') then
            add_token(token.INT, tonumber(match(2), 16))
        elseif scan('^%-?%d+') then
            -- scanned an integer so far
            local t = token.INT
            if scan('^%.%d*') then
                -- scanned a fraction part
                t = token.FLOAT
            end
            if scan_exponent() then
                -- scanned an exponential part
                t = token.FLOAT
            end
            add_token(t, tonumber(match()))
        elseif scan('^%-?%.%d+') then
            -- scanned a fractional part without leading integral part.  scan
            -- for an optional exponential part.
            scan_exponent()
            add_token(token.FLOAT, tonumber(match()))
        elseif scan('^[!@#$%%^&*%-+=;\\,.?/]') or scan_compare() then
            add_token(token.OP)
        else
            -- report lexical error and skip character.
            report_error()
            pos = pos + 1
        end
    end

    -- add final EOS token.
    add_token(token.EOS)

    return tokens, errors
end

return {
    token = token,
    lex = lex,
}
