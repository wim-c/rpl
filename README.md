# RPL21
RPL21 (or Reverse Polish Language 2021) is a programming language inspired by
the RPL language for Commodore PET/CBM machines in the early eighties.  That
original language and a development system that came with it was programmed by
Tim Stryker and sold by his company Samurai Software.  Although the Commodore
PET was my first computer back in 1979, I'd never heard of RPL until the summer
of 2020.  I was immediately captured by its goal to be better performing and
more compact than BASIC and friendlier than Forth.

So I decided to build my onw compiler and interpreter for an RPL inspired
language as a pet project for the 2020 summer holidays.  The first version
stayed fairly close to the original, both in concepts and syntax.  It was a joy
to see compiled programs run on Commodore PET and 64 machines.

Then in the summer of 2021, after playing around a fair bit with that first
version, I decided to significantly alter the language.  The compiler was
completely rewritten.  This rewritten version is now called RPL21.

Note that I do not have the original RPL compiler or runrime or any RPL program
for that matter.  The only source and inspiration for my work is the original
RPL manual and some scattered magazine arcticles, including ones by the author
Tim Stryker himself.

## RPL21 versus RPL
So what are the main differences between RPL21 and the original RPL?  First of
all, RPL21 is a cross compiler. This means that the compiler does not run on
the original Commodore hardware but instead on any machine supporting Python3.
The byte code that is produced can be loaded onto a Commodore PET or 64 and
executed by the RPL21 interpreter written in 6502/6510 assembly.

RPL21 retains the single BASIC token approach to keywords as RPL did and most
keywords have the same syntax.  RPL21 adds a few additional keywords to the
language such as ON, and more comparison operators.  The byte code produces by
RPL21 is not compatible with the original RPL byte code.  In fact, I do not
even know the original RPL byte codes.

RPL21 will not put strings on the parameter stack.  Instead, a string is
represented on the parameter stack by its address.  RPL21 also supports
floating point literals, which will be compiled to five bytes of data, in the
same format as used by Commodore BASIC.  The five byte floating point data is
never pushed onto the parameter stack but instead the address of a floating
point value will be pushed.  There is no arithmetic support for floating point
in RPL21.  Use BASIC ROM routines for that if needed.

RPL21 does not integrate with BASIC programs in the same seamless was as RPL
did.  An RPL21 program cannot contain lines of BASIC and a BASIC program cannot
switch to RPL21 with a GO command, as RPL allowed.  Instead, an RPL21 byte code
program can be executed by a SYS call to the address where the program is
loaded.

RPL21 is a more structured language than RPL.  It supports procedure calls,
macros, and scoped (label) definitions.  Also, RPL21 strictly separates data
from program code.  This means that data cannot be inlined in code and will
also never be silently executed as byte code.  It is still possible to execute
data, if you absolutely must, by an explicit GOTO or GOSUB to a label inside a
data segment.

RPL21 uses an optimizing compiler.  In particular, the byte code that it
produces may differ quite a bit from the program code from which it was
compiled.  For example, constant expressions may be computed compile time,
unreachable code will be eliminated, conditional statements may be reshuffled,
and tall calls are replaced by jumps, and so on..

## The RPL21 language
This section describes all RPL21 commands and statements.  RPL21 accepts both
the lower case and upper case form of all keywords, but not mixed cases.  For
example, "FOR" and "for" indicate the same keyword, while "For" will be
interpreted as an identifier instead. 

Each parameter stack entry is a 16-bit word (so two bytes each).  All
arithmetic and string conversion operations treat parameter stack entries as
signed words, in two's complement form.  Operators that require an address,
such as @ (fetch) and ! (store) consider a parameter stack entry as an unsigned
word.

### AND
Pop the tos and nos and push their bitwise AND value on the stack.

### CONT IF
Pop the tos.  If it is not equal to zero then continue with the code directly
following the CONT IF statement.  Otherwise, jump to the first THEN or END in
the same scope following the CONT IF statement or to the end of the program if
neither a THEN or END is present.  This is a useful construct to implement
short-circuiting conditional statements or "else if" constructions as known in
some other languages.  This can prevent nested IF statements, making the code
more concise and readable.  Here are some examples:

```basic
    REM test if tos is between 10 and 20 inclusive.
    # 10 >= IF # 20 <= CONT IF
        REM tos is between 10 and 20.
    END

    REM take different actions based on the tos.
    # 1 = IF
        REM tos equals 1.
    THEN # 2 = CONT IF
        REM tos equals 2.
    THEN # 3 = CONT IF
        REM tos equals 3.
    THEN
        REM tos has some other value.
    END
```

### CHR$
Pop tos and convert it as an unsigned word to a hexadecimal string.  Push the
address of the string.  The string will not have leading zeroes and is stored
in a temporary buffer.  Note that this buffer will be overwritten by a next
call to CHR$, STR$, or INPUT so the string must be copied to somewhere else if
you need to use it again later.

### CLR
Should only be used when a FOR loop is executing.  Drop the inner most FOR loop
scope.  This is useful if you want to stop a FOR loop before it reaches its
final counter value.  Note that CLR does not imply a jump (e.g. to some NEXT
statements) but program execution will continue as usual.  If more then one FOR
loop is nested then only then inner most loop is affected.  All other loops
counters retain their current value.

### DATA .. END
Defines an anonymous inline block of contiguous data and pushes its address on
the parameter stack.  See the LET statement for how to bind a data block to a
label instead.  The data block does not introduce a new scope so any label that
is defined in the body of the block is visible from outside the data block.
Any number of entries of the following kinds may appear in any order in the
body of the data block:

 * A word block [ .. ]
 * A byte block ( .. )
 * A string literal ".."
 * A character array literal '..'
 * A floating point constant

The content of the items in the data block body is then concatenated to one
contiguous block.  The following example shows a data block and its output when
compiled:

```basic
    REM an example of a contiguous data block. 
    DATA
        [1 2 3 4]
        (5 6 7 8)
        "foo"
        'bar'
        3.1415 0.1
        [10 "baz" 'chars' 1.414]  REM note the nested data here.
    END
```

This leads to the emitted byte data in a compiled program below.  Note that the
string, char array, and floating point data in the last word block is still
encoded by reference because it does not appear on top level in the data block.

```
    1000 data.1:
    1000 01 00          1
    1002 02 00          2
    1004 03 00          3
    1006 04 00          4
    1008 05             5
    1009 06             6
    100a 07             7
    100b 08             8
    100c 03 66 6f 6f    "foo"
    1010 62 61 72       'bar'
    1013 82 49 0e 56 04 3.1415
    1018 7d 4c cc cc cd 0.1
    101d 0a 00          10
    101f 25 10          string.1
    1021 29 10          chars.1
    1023 2e 10          float.1

    1025 string.1:
    1025 03 62 61 7a    "baz"

    1029 chars.1:
    1029 63 68 61 72 73 'chars'

    102e float.1:
    102e 81 34 fd f3 b6 1.414
```

### DEF .. END
Defines an anonymous inline procedure and pushes its address on the parameter
stack.  See the LET statement for how to bind a procedure to a label instead.
The procedure defines its own scope, that is, the code in the procedure can use
all the names from the scope in which the procedure appears but labels defined
inside the procedure are only visible in the scope of the procedure itself.  A
procedure has an implicit RETURN command just before its closing END keyword,
so an explicit RETURN is only required to return from an producedure before
reaching the end of its code block.

### FN
Should only be used when a FOR loop is executing.  Pushes the current value of
the inner most loop counter onto the parameter stack.

### FOR
Prepare a new FOR loop with a counter starting at tos and ending at nos
(inclusive).  Pop tos and nos.  Code executions continues directly after the
FOR command.

### GET
Read a character from the keyboard buffer and push its value onto the
parameters stack.  Push a zero value if no character is available.  This
command does not wait for keyboard input.  Loop until tos is non-zero to wait
for character input.

### GOSUB (or &)
Store the current program counter, pop tos and continue code execution at that
address.  Note that the program counter is stored on the CPU stack, not on the
parameter stack.

### GOTO
Pup tos and continue code execution at that address.

### INPUT
Show a cursor and wait until a line is entered (until the enter key is
pressed).  The entered string is stored in a temporary buffer and its address
is pushed onto the parameter stack.  Note that the temporary buffer is shared
with the CHR$ and STR$ commands, so the string must be copied to somewhere else
if you need it later.

### INT
Swap the high- and low bytes of tos.

### NEXT
Should only be used when a FOR loop is executing.  Check the inner most FOR
loop counter.  If it equals its end value (as set by the FOR command) then drop
the FOR loop scope and continue to the next statement.  Otherwise, increment
the loop counter by one and jump to directly after the FOR statement.  Note
that FOR and NEXT are two separate commands and do not define a syntactic
scope.

### NOT
Flip all bits of tos.  That is, exclusive or the value of tos with $FFFF.

### ON
Compute the effective address A as tos plus two times nos.  Pop tos and nos and
push the word at address A.  This is useful to easily GOTO or GOSUB different
locations based on a value on the parameters stack.  Here is a typical example:

```basic
    REM execute different procedures, based on the value at tos.
    [proc0 proc1 proc2] ON GOSUB

    LET proc0 DEF
        REM executed when tos = 0
    END

    LET proc1 DEF
        REM executed when tos = 1
    END

    LET proc2 DEF
        REM executed when tos = 2
    END
```

### OR
Pop tos and nos and push their bitwise OR value.

### PEEK
Pop tos as an address (unsigned word) and push the byte at that address.  The
high byte of the result at tos will be zero.

### POKE
Pop tos as an address (unsigned word) and store the low byte of nos at that
address.  Pop nos.

### PRINT
Pop tos as a string address (unsigend word) and print the string.  Note that
the output does not include a newline.  If a newline is required then Either
include it in the string or print it separately.

### RETURN
Should only be used if a GOSUB (or &) command was executed earlier.  Pops an
address from the CPU stack (not from the parameter stack) and sets it as the
current program counter.  Program execution continues from this new program
counter.

### RND
Pushes a random signed word on the parameter stack.  All values can occur.  The
period of the RND command is 16,777,215.

### STOP
Stop program execution and return to BASIC.

### STR$
Pop tos as a signed word and convert it to a string.  Push the address of the
string.  Note that unlike in BASIC, non-negative values will not have a leading
space in their string representation.  The string is stored in a temporary
buffer that is shared with the CHR$ and INPUT commands so it must be copied to
another location if it is needed later.

### SYS
Pop tos as an address (unsigned word) and execute machine code starting at that
address.  An RTS instriction will resume normal program execution directly
following the SYS command.
