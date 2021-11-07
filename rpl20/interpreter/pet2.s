
;
; Definitions for Commodore PET Basic 2.0
;

; Location of the interpreter (ROM area).
!address org = $9000

; Parameter stack page.  The entire page is used as a stack of word registers.
; Lo and hi bytes of each word are stored in separate halves of the page.  This
; requires a little less operations with the index register x that is used as a
; parameter stack pointer.
!address pslo = $7f00
!address pshi = $7f80

; Initial parameter stack pointer.  Note that the parameter stack is split into
; two sections for lo and hi bytes of each word, and each section is half a
; page large..
pstop = $7f

; Scratch area where the stack pointer is saved when the byte code interpreter
; is invoked.  The stack pointer is reset to this position when the byte code
; interpreter returns.
!address saves = $a2

; Scratch areas to save registers.
!address savex = $0f
!address savey = $10

; Indirect jmp instruction to the byte code handler is setup here.
!address trampoline = $fd
!address dispatch = $fe

; Program counter.  The low byte of this pc is always 0.  The actual low byte
; of the program counter is stored in the y register.
!address pc = $01

; Scratch area to store an effective address (or a register for arithmetic).
!address ea = $11

; Two 16 bit registers for arithmetic.
!address lw = $67
!address hw = $69

; Location where stop key scanline value is stored and the scan value of the
; stop key.
!address stop_scan = $9b
stop_value = $ef

; Location of the three bytes random state used by the rnd command.  This is
; part of the location that is used for the random number generator in BASIC.
!address rnd = $8a

; Input buffer location.  Assumed to accomodate at least 81 characters.
!address INBUF = $200

; Location of three byte jiffy counter (big endian).
!address jiffy = $8d

; KERNAL entries
!address CHRIN = $ffcf
!address CHROUT = $ffd2
!address GETIN = $ffe4
