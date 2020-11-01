# RPL

This is a stack oriented programming language for the 6502 family of processors.  It is not te be confused with an equally named language for HP calculators.  Instead, it is inspired by the RPL language developed by [Tim Stryker](https://en.wikipedia.org/wiki/Tim_Stryker) and published by his company Samurai Software for the [Commodore PET](https://en.wikipedia.org/wiki/Commodore_PET) in 1981.  A manual of that language can be found [here](https://portcommodore.com/dokuwiki/lib/exe/fetch.php?media=larry:comp:flash_attack:fa-rplmaual.pdf).

## About this implementation

This implementation is based on the original manual of Samurai Software's RPL as linked above.  The best way to start with RPL is to read that manual.  I do not have an actual copy of the original language and never used it in any way.  Back in the day I was already very interested in computer languages that ran on my Commodore PET (and later CBM) such as Forth and COMAL.  However, I had never heard of the RPL language until the summer of 2020 and liked its ideas so much that I decided to start a pet project to recreate it.

RPL consists of a compiler that compiles an RPL source file to byte code and a byte code interpreter that executes the byte code.  The compiler is a cross-compiler in the sense that it does not run on vintage Commodore computers but consists of a number of Lua scripts that you can use on any system that runs Lua.  (The original RPL compiler was written in RPL.)  The compiler can produce either a human readable output listing or a binary byte code file.  The byte code interpreter is written in 6502 assembly and weighs in well under 2K.

## Differences to the orginal RPL

Almost all of the original RPL commands are supported and have the same behavior.  The only exception is the `new` command that I intend to repurpose together with `fre` to add dynamic memory management to RPL in a future update.  Originally the `new` command cleared the parameter stack but in the current version it is not supported and should not be used.  The logical operators `<=`, `>=`, and `<>` have been added.

String handling is completely different.  The original RPL pushes strings onto the parameters stack, using a word for each character and the string length.  In my version, strings are never pushed onto the stack.  Instead, when a string appears as a command (so not in a data segment) then that string is implicitly added as data to the program and the address of that string is pushed on the parameter stack.  For example the (fairly useless) program

```
"HELLO WORLD!" stop
```

Pushes the address of the string onto the parameter stack and stops execution.  The string itself consists of a single unsigned byte indicating its length, followed by the characters that make up the string.  Here is the compiled listing of this program:

```
0900 20 00 C1       start interpreter at $C100
0903 09 06          push string.1
0905 F2             stop

0906 string.1:
0906 0C 48 45 4C 4C string 'HELLO WORLD!'
090B 4F 20 57 4F 52
0910 4C 44 21      
```

Incidentally, this example shows why it is important to explicitly `stop` the execution of an RPL program.  If it were omitted then execution would happily continue into the string data at address `$906`.  Just like the original, there is no hand holding in RPL!

Commands that return a string (`input`, `str`, and `chr`) push the address of a temporary buffer that holds the string.  This buffer is reused, so make sure to process a string result before using any of these commands again.
