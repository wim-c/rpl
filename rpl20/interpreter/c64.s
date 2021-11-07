
;
; Definitions for Commodore 64
;

; Location of the interpreter.
!address org = $c100

; Parameter stack page.  The entire page is used as a stack of word registers.
; Lo and hi bytes of each word are stored in separate halves of the page.  This
; requires a little less operations with the index register x that is used as a
; parameter stack pointer.
!address pslo = $c000
!address pshi = $c080

; Initial parameter stack pointer.  Note that the parameter stack is split into
; two sections for lo and hi bytes of each word, and each section is half a
; page large..
pstop = $7f

; Scratch area where the stack pointer is saved when the byte code interpreter
; is invoked.  The stack pointer is reset to this position when the byte code
; interpreter returns.
!address saves = $fb

; Scratch areas to save registers.
!address savex = $03
!address savey = $04

; Indirect jmp instruction to the byte code handler is setup here.
!address trampoline = $fc
!address dispatch = $fd

; Program counter.  The low byte of this pc is always 0.  The actual low byte
; of the program counter is stored in the y register.
!address pc = $05

; Scratch area to store an effective address (or a register for arithmetic).
; This is the location that is also used by the BASIC SYS command to store the
; target address.
!address ea = $14

; Two 16 bit registers for arithmetic.
!address lw = $6b
!address hw = $6d

; Location where stop key scanline value is stored and the scan value of the
; stop key.
!address stop_scan = $91
stop_value = $7f

; Location of the three bytes random state used by the rnd command.  This is
; part of the location that is used for the random number generator in BASIC.
!address rnd = $8d

; Input buffer location.  Assumed to accomodate at least 81 characters.
!address INBUF = $200


; BASIC entries

; Entry point in the SYS command with the target address already loeaded in ea.
; Gets registers and status register from memory, executes the subroutine, and
; places the registers and status register back in memory.
!address SYS = $e130

; KERNAL entries
!address RDTIM = $ffde
!address CHRIN = $ffcf
!address CHROUT = $ffd2
!address GETIN = $ffe4
