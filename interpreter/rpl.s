
;
; Choose a target on which the interpreter will run.
;

target_pet2
; target_c64


;
; Read target specific definitions.
;

!ifdef target_pet2 {
    !src "pet2.s"
} else ifdef target_c64 {
    !src "c64.s"
} else {
    !error "No target specified."
    !eof
}


; Set location of interpreter.
* = org

; Alias for the jmp indirect instruction.
jmpi = $6c

; Initial parameter stack pointer.  Note that the parameter stack is split into
; two sections for lo and hi bytes of each word, and each section is half a
; page large..
pstop = $7f

; Hardware stack page.
!address st = $100

;
; Entry point of interpreter.
;
            ; Clear decimal mode.
            cld

            ; Prepare trampoline.
            lda #jmpi       ; Prepare indirect jump instruction.
            sta trampoline
            lda #>jumptab   ; Prepare hi byte of effective address.
            sta dispatch+1

            ; Seed the random state (from the jiffy clock).
!ifdef RDTIM {
            jsr RDTIM       ; Get time in y;x;acc.
            ora #1          ; Make sure that the seed is not zero.
} else ifdef jiffy {
            lda jiffy+2     ; Get time from jiffy counter.
            ldx jiffy+1
            ldy jiffy
            ora #1          ; Make sure that the seed is not zero.
} else {
            lda #$11        ; Some arbitrary initial non-zero random seed.
            ldx #$55
            ldy #$aa
}
            sta rnd
            stx rnd+1
            sty rnd+2

            ; Prepare pc.
            pla             ; Get lo byte of return address.
            tay             ; Set it as pc offset in the y register.
            pla             ; Get hi byte of return address.
            sta pc+1        ; Set it as hi byte of pc.
            lda #0          ; Clear lo byte of pc (indexed by y register).
            sta pc

            ; Save stack pointer.
            tsx
            stx saves

            ; Prepare parameter stack pointer.
            ldx #pstop

            ; Start decode loop.
            bne decodenext

;
; Stop the interpreter.
;
exec_stop   ldx saves       ; Restore stack pointer.
            txs
            rts             ; Return to calling code.

;
; Helper code to increment pc when crossing a page boundary during decoding.
;
--          inc pc+1
            bne decode
-           inc pc+1
            bne +

;
; Fetch next opcode.  Entry point is decode when pc already points at the next
; opcode to fetch.
;
decodenext  iny             ; Increment pc.
            beq --          ; Handle page boundary.
decode      lda stop_scan   ; Check if stop key is pressed
            cmp #stop_value
            beq exec_stop   ; Stop interpreter if stop key pressed.
            lda (pc),y      ; Get opcode.
            iny             ; Skip opcode.
            beq -           ; Handle page boundary.
+           cmp #$c0        ; Check if opcode is a push operator
            bcc push        ; If so then handle the push.

;
; Dispatch operator
;
            asl             ; Multiply opcode by two to get its index in the
                            ; jump table.  This index always has bit 7 set so
                            ; the jump table must start at an address of the
                            ; form $xx80.
            sta dispatch    ; Set as lo byte of the dispatch.
            jmp trampoline  ; Trampoline to handler code.

;
; Handle push operators.
;
push        cmp #$80        ; Check if it is a 15-bit word.
            bcc push15      ; If so then handle it as such.

;
; Push 6-bit signed word.  The opcode has the form %10aa_bbbb and encodes the
; signed 6 bit word aa_bbbb.
;
            cmp #$a0        ; Check sign of 6-bit word.
            bcs +           ; Branch if negative.
            and #$3f        ; Keep the numeric part.
            sta pslo,x      ; Place value in tos.
            lda #0          ; Clear hi byte.
-           sta pshi,x
            dex
            jmp decode      ; Decode next opcode.
+           ora #$c0        ; Sign extend negative word.
            sta pslo,x      ; Place value in tos.
            lda #$ff        ; Sign extend hi byte.
            bne -           ; Branch always.

;
; Push 15-bit signed word.  The opcode and its single byte parameter have the
; form %0aaa_bbbb %cccc_dddd and together encode the signed 15 bit word
; aaa_bbbb_cccc_dddd.
;
push15      cmp #$40        ; Check sign.
            bcc +           ; Branch if positive.
            ora #$80        ; Sign extend word.
+           sta pshi,x      ; Place value in tos.
            lda (pc),y
            sta pslo,x
            dex
            jmp decodenext  ; Decode next opcode.

;
; Operator jump table.
;

; Align jump table on $xx80 address.
* = ((* + $7f) & $ff00) | $80

!address jumptab = *

; Opcode jump table starting from byte code $80 upward.
!word exec_pusha
!word exec_pushn
!word exec_pushp
!word exec_add
!word exec_and
!word exec_beqa
!word exec_beqn
!word exec_beqp
!word exec_bnea
!word exec_bnen
!word exec_bnep
!word exec_call
!word exec_calla
!word exec_calln
!word exec_callp
!word exec_chr
!word exec_clr
!word exec_div
!word exec_drop
!word exec_dup
!word exec_eq
!word exec_fetch
!word exec_fn
!word exec_for
!word exec_ge
!word exec_get
!word exec_goto
!word exec_gotoa
!word exec_goton
!word exec_gotop
!word exec_gt
!word exec_input
!word exec_int
!word exec_le
!word exec_lt
!word exec_mod
!word exec_mul
!word exec_ne
!word exec_new
!word exec_next
!word exec_not
!word exec_or
!word exec_over
!word exec_peek
!word exec_pick
!word exec_poke
!word exec_print
!word exec_return
!word exec_rnd
!word exec_roll
!word exec_stop
!word exec_store
!word exec_str
!word exec_sub
!word exec_swap
!word exec_sys

;
; Push absolute word.  The two byte parameter encodes the word in big endian.
;
exec_pusha      lda (pc),y      ; fetch hi byte of word
                sta pshi,x      ; push hi byte
                iny             ; increment pc
                beq +           ; handle page boundary
-               lda (pc),y      ; push lo byte
                sta pslo,x
                dex
                jmp decodenext  ; decode next opcode
+               inc pc+1
                bne -
;
; Push backward relative word.  Pushes the word address-offset where address is
; the address of the opcode and offset is encoded as an unsigned single byte
; parameter.
;
exec_pushn      tya             ; Subtract argument+1 from pc.
                clc
                sbc (pc),y
                sta pslo,x      ; Push lo byte.
                lda pc+1        ; Push hi byte.
                sbc #0
                sta pshi,x
                dex
                jmp decodenext  ; Decode next opcode.

;
; Push forward relative word.  Pushes the word address+2+offset where address
; is the address of the opcode and offset is encoded as an unsigned single byte
; parameter.
;
exec_pushp      tya             ; Add argument+1 to pc.
                sec
                adc (pc),y
                sta pslo,x      ; Push lo byte.
                lda pc+1        ; push hi byte
                adc #0
                sta pshi,x
                dex
                jmp decodenext  ; Decode next opcode.

;
; Pop tos and nos and push their sum.
;
exec_add        inx
                clc
                lda pslo+1,x
                adc pslo,x      ; Add lo bytes of nos and tos.
                sta pslo+1,x    ; Store as lo byte of nos.
                lda pshi+1,x
                adc pshi,x      ; Add hi bytes of nos and tos.
                sta pshi+1,x    ; Store as hi byte of tos.
                jmp decode      ; Decode next opcode.

;
; Pop tos and nos and push (tos AND nos).
;
exec_and        inx
                lda pslo+1,x
                and pslo,x      ; Logical and of lo bytes of nos and tos.
                sta pslo+1,x    ; Store as lo byte of nos.
                lda pshi+1,x
                and pshi,x      ; Logical and of hi bytes of nos and tos.
                sta pshi+1,x    ; Store as hi byte of nos.
                jmp decode      ; Decode next opcode.

;
; Pop tos and test if it is zero.  Result in z flag.
;
iszero          inx
                lda pslo,x      ; Pull lo byte.
                ora pshi,x      ; Pull hi byte and derive z from (lo OR hi).
                rts

;
; Pop tos and set it as pc.
;
exec_goto       inx
                lda pslo,x      ; Pull lo byte.
                tay             ; Set pc offset.
                lda pshi,x      ; Pull hi byte.
                sta pc+1        ; Set pc page.
                jmp decode      ; Decode next opcode.

;
; Set pc to address encoded as big endian word parameter.
;
exec_gotoa      lda (pc),y      ; Get hi byte.
                sta pc+1        ; Store as page of pc.
                iny             ; Increment pc.
                beq +           ; Handle page boundary.
-               lda (pc),y      ; Get lo byte.
                tay             ; Set pc offset.
                jmp decode      ; Decode next opcode.
+               inc pc+1
                bne -

;
; Set pc to address-offset where address is the address of the opcode and
; offset is encoded as an unsigned single byte parameter.
;
exec_goton      tya             ; Subtract offset+1 from pc.
                clc
                sbc (pc),y
                tay             ; Set pc offset.
                bcs +
                dec pc+1        ; Correct for page boundary.
+               jmp decode      ; Decode next opcode.

;
; Set pc to address+2+offset where address is the address of the opcode and
; offset is encoded as an unsigned single byte parameter.
;
exec_gotop      tya             ; Add offset+1 to pc.
                sec
                adc (pc),y
                tay             ; Set pc offset.
                bcc +
                inc pc+1        ; Correct for page boundary.
+               jmp decode      ; Decode next opcode.

;
; Pop tos and branch to target if it is zero.  Target is encoded as a two byte
; big endian parameter.
;
exec_beqa       jsr iszero      ; Test and pop tos.
                beq exec_gotoa  ; Goto address if zero.
skip_hi         iny             ; Skip hi byte of operand.
                beq +           ; handle page boundary
                jmp decodenext  ; Decode next opcode.
+               inc pc+1
                jmp decodenext

;
; Pop tos and branch to target if it is zero.  Target equals address-offset
; where address is the address of the opcode and offset is encoded as an
; unsigned single byte parameter.
;
exec_beqn       jsr iszero      ; Test and pop tos.
                beq exec_goton  ; Goto backward relative address if zero.
                jmp decodenext  ; Skip operand and decode next opcode.

;
; Pop tos and branch to target if it is zero.  Target equals address+2+offset
; where address is the address of the opcode and offset is encoded as an
; unsigned single byte parameter.
;
exec_beqp       jsr iszero      ; Test and pop tos.
                beq exec_gotop  ; Goto forward relative address if zero.
                jmp decodenext  ; Skip operand and decode next opcode.

;
; Pop tos and branch to target if it is non-zero.  Target is encoded as a two
; byte big endian parameter.
;
exec_bnea       jsr iszero      ; Test and pop tos.
                bne exec_gotoa  ; Goto address if not zero.
                beq skip_hi     ; Skip operand and decode next opcode.

;
; Pop tos and branch to target if it is non-zero.  Target equals address-offset
; where address is the address of the opcode and offset is encoded as an
; unsigned single byte parameter.
;
exec_bnen       jsr iszero      ; Test and pop tos.
                bne exec_goton  ; Goto backward relative address if not zero.
                jmp decodenext  ; Skip operand and decode next opcode.

;
; Pop tos and branch to target if it is non-zero.  Target equals
; address+2+offset where address is the address of the opcode and offset is
; encoded as an unsigned single byte parameter.
;
exec_bnep       jsr iszero      ; Test and pop tos.
                bne exec_gotop  ; Goto forward relative address if not zero.
                jmp decodenext  ; Skip operand and decode next opcode.

;
; Push next-1 on return stack, pop tos and set it as pc.  Here next is the
; address of the next opcode.
;
exec_call       tya             ; Push pc-1 as return address.
                sec
                sbc #1
                sta ea
                lda pc+1
                sbc #0
                pha
                lda ea
                pha
                jmp exec_goto   ; Goto address on parameter stack.

;
; Push next-1 on return stack and set pc to target.  Here next is the address
; of the next opcode and target is encoded as a two byte big endian parameter.
;
exec_calla      tya             ; Push pc+1 as return address.
                clc
                adc #1
                sta ea
                lda pc+1
                adc #0
                pha
                lda ea
                pha
                jmp exec_gotoa  ; Goto address.

;
; Push next-1 on return stack and set pc to target.  Here next is the address
; of the next opcode and target is next-2-offset where offset is encoded as an
; unsigned single byte parameter.
;
exec_calln      lda pc+1        ; Push pc as return address.
                pha
                tya
                pha
                jmp exec_goton  ; Goto backward relative address.

;
; Push next-1 on return stack and set pc to target.  Here next is the address
; of the next opcode and target is next+offset where offset is encoded as an
; unsigned single byte parameter.
;
exec_callp      lda pc+1        ; Push pc as return address.
                pha
                tya
                pha
                jmp exec_gotop  ; Goto forward relative address.

;
; Helper code to transform input byte in y register into hex character in acc.
;
hi_ascii        tya             ; Copy input to acc.
                lsr             ; Shift hi nibble to lo nibble.
                lsr
                lsr
                lsr
                bpl +           ; Branch always
lo_ascii        tya             ; Copy input to acc.
                and #$f         ; Clear hi nibble.
+               ora #'0'        ; Add offset for numeric values.
                cmp #$3a        ; Check if value is numeric.
                bcc +           ; Branch if numeric.
                adc #'A'-'0'-11 ; Add offset for alphanumeric character.
+               rts

;
; Convert tos as an unsiged word to four hexadecimal digits string.  The string
; is always created at the same location, overwriting any previous value.
; Drops tos and pushes the address of the string.
;
exec_chr        sty savey       ; Save y register.
                inx
                ldy pshi,x      ; Convert hi byte to hex an add two characters
                jsr hi_ascii    ; to the input buffer.
                sta INBUF+1
                jsr lo_ascii
                sta INBUF+2
                ldy pslo,x      ; Convert lo byte to hex an add two characters
                jsr hi_ascii    ; to the input buffer.
                sta INBUF+3
                jsr lo_ascii
                sta INBUF+4
                ldy savey       ; Restore y register
                lda #4          ; Set string length.
                sta INBUF
                lda #>INBUF     ; Overwrite tos with address of string.
                sta pshi,x  
                lda #<INBUF
                sta pslo,x
                dex
                jmp decode      ; Decode next opcode.

;
; Pop current index, upper bound, and address of for block from the return
; stack.
;
exec_clr        stx savex       ; Save x register.
                tsx             ; Drop three words from return stack.
                txa
                clc
                adc #6
                tax
                txs
                ldx savex       ; Restore x register.
                jmp decode      ; Decode next opcode.

;
; Routine to compute quotient and remainder of abs(nos) divided by abs(tos).
; Drops tos.  The quotient and remainder are left in lw and hw respectively.
;
; The entry point divmod_tos can be used if only the numerator needs to be
; taken from tos and the denominator is already stored in ea.  In this case tos
; remains (unchanged) on the stack,
;
; The entry point divmod_only can be used when both numerator and denominator
; are already stored in lw and ea respectively.
;
divmod          inx             ; Store denominator in ea.
                lda pslo,x
                sta ea
                lda pshi,x
                sta ea+1
                bpl divmod_tos  ; Branch if non-negative.
                sec             ; Negate ea.
                lda #0
                sbc ea
                sta ea
                lda #0
                sbc ea+1
                sta ea+1
divmod_tos      inx
                lda pslo,x      ; Store numerator in lw.
                sta lw
                lda pshi,x  
                sta lw+1
                bpl divmod_only ; Branch if non-negative.
                sec             ; Negate lw.
                lda #0
                sbc lw
                sta lw
                lda #0
                sbc lw+1
                sta lw+1
divmod_only     lda #0          ; Clear hw.
                sta hw
                sta hw+1
                stx savex       ; Save registers.
                sty savey

                ; Division loop.
                ldx #16         ; Loop counter.
-               asl lw          ; Asl dword hw;lw.
                rol lw+1
                rol hw
                rol hw+1
                sec             ; Compute hw-ea and store in a;y.
                lda hw
                sbc ea
                tay
                lda hw+1
                sbc ea+1
                bcc +           ; Branch if ea > hw.
                sty hw          ; Store difference in hw.
                sta hw+1
                inc lw          ; Shift result into lw.
+               dex             ; Repeat 16 times.
                bne -

                ; Finish up.
                ldx savex       ; Restore registers.
                ldy savey
                rts

;
; Compute quotient of nos divided by tos and round to zero.  Drops tos and nos
; and pushes the result.
;
exec_div        jsr divmod      ; Compute quotient and remainder.
                dex             ; Restore nos.
                lda pshi,x      ; Check sign of result.  (Bit 15 of tos EOR bit
                eor pshi+1,x    ; 15 of nos).
                bmi +           ; Branch if result is negative.
                lda lw          ; Push lo byte of quotient.
                sta pslo+1,x
                lda lw+1        ; Push hi byte of quotient.
                sta pshi+1,x
                jmp decode      ; Decode next opcode.
+               sec             ; Negate and push result.
                lda #0          ; Push lo byte of negated quotient.
                sbc lw
                sta pslo+1,x
                lda #0          ; Push hi byte of negated quotient.
                sbc lw+1
                sta pshi+1,x
                jmp decode      ; Decode next opcode.

;
; Drop tos.
;
exec_drop       inx             ; Drop tos.
                jmp decode      ; Decode next opcode.

;
; Duplicate tos.
;
exec_dup        lda pshi+1,x    ; Push hi byte.
                sta pshi,x
                lda pslo+1,x    ; Push lo byte.
                sta pslo,x
                dex
                jmp decode      ; Decode next opcode.

;
; Support routine for signed comparison operators.  Drop tos and nos and push 0
; if (v EOR n) is set, or -1 otherwise.
;
binge           bvs +           ; If overflow then n flag holds result.
                eor #$80        ; Negate n flag (note next branch is taken).

;
; Support routine for signed comparison operators.  Drop tos and push -1 if
; (v EOR n) is set, or 0 otherwise.
;
binlt           bvc +           ; If no overflow then n flag holds result.
                eor #$80        ; Negate n flag.
+               bmi bintrue     ; If ge (or lt) and flags indicate >= (or <)
                                ; set result to -1.  Otherwise set result to 0.
binfalse        lda #0          ; Load false byte.
                beq +           ; Skip next instruction.
bintrue         lda #$ff        ; Load true byte.
+               sta pslo+1,x    ; Set tos to 0 or -1.
                sta pshi+1,x
                jmp decode      ; Decode next opcode.

;
; Drop tos and nos.  Push -1 (true) if nos <= tos or 0 (false) otherwise.
;
exec_le         inx
                lda pslo,x      ; Compare tos to nos.
                cmp pslo+1,x
                lda pshi,x
                sbc pshi+1,x
                jmp binge       ; True if tos greater or equal nos.

;
; Drop tos and nos.  Push -1 (true) if nos < tos or 0 (false) otherwise.
;
exec_lt         inx
                lda pslo+1,x    ; Compare nos to tos.
                cmp pslo,x
                lda pshi+1,x
                sbc pshi,x
                jmp binlt       ; True if nos less than tos.

;
; Drop tos and nos.  Push -1 (true) if nos >= tos or 0 (false) otherwise.
;
exec_ge         inx
                lda pslo+1,x    ; Compare nos to tos.
                cmp pslo,x
                lda pshi+1,x
                sbc pshi,x
                jmp binge       ; True if nos greater or equal tos.

;
; Drop tos and nos.  Push -1 (true) if nos > tos or 0 (false) otherwise.
;
exec_gt         inx
                lda pslo,x      ; Compare tos to nos.
                cmp pslo+1,x
                lda pshi,x
                sbc pshi+1,x
                jmp binlt       ; True if tos less than nos.

;
; Drop tos and nos.  Push -1 (true) if nos == tos or 0 (false) otherwise.
;
exec_eq         inx
                lda pslo,x      ; Compare lo bytes.
                cmp pslo+1,x
                bne binfalse    ; False if bytes differ.
                lda pshi,x      ; Compare hi bytes.
                cmp pshi+1,x
                bne binfalse    ; False if btes differ.
                beq bintrue     ; True if tos equals nos.

;
; Drop tos and nos.  Push -1 (true) if nos != tos or 0 (false) otherwise.
;
exec_ne         inx
                lda pslo,x      ; Compare lo bytes.
                cmp pslo+1,x
                bne bintrue     ; True if bytes differ.
                lda pshi,x      ; Compare hi bytes.
                cmp pshi+1,x
                bne bintrue     ; True if bytes differ.
                beq binfalse    ; False if tos equals nos.

;
; Pop tos and push word at address given by tos.
;
exec_fetch      inx
                lda pslo,x      ; Copy tos to ea.
                sta ea
                lda pshi,x
                sta ea+1
                sty savey       ; Save y register.
                ldy #0          ; Push lo byte at ea.
                lda (ea),y
                sta pslo,x
                iny             ; Push hi byte at ea.
                lda (ea),y
                sta pshi,x
                dex
                ldy savey       ; Restore y register.
                jmp decode      ; Decode next opcode.

;
; Push current index at top of return stack onto the parameter stack.
;
exec_fn         sty savey       ; Save y register.
                txa             ; Copy param stack pointer to y register.
                tay
                tsx             ; Copy return stack pointer to x register.
                inx
                lda st+1,x      ; Push hi byte.
                sta pshi,y
                lda st,x        ; Push lo byte.
                sta pslo,y
                tya             ; Restore param stack pointer.
                tax
                dex
                ldy savey       ; Restore y register.
                jmp decode      ; Decode next opcode.

;
; Push next, nos, and tos on the return stack where next is the address of the
; next opcode.
;
exec_for        lda pc+1        ; Push program counter of the first opcode in.
                pha             ; The for block.
                tya
                pha
                inx
                lda pshi+1,x    ; Push upper bound of range.
                pha
                lda pslo+1,x
                pha
                lda pshi,x      ; Push current loop index.
                pha
                lda pslo,x
                pha
                inx             ; Drop tos and nos.
                jmp decode      ; Decode next opcode.

;
; Get a key from keyboard queue, or 0 if the queue is empty, and push it as an
; unsigned byte.
;
exec_get        stx savex       ; Save registers.
                sty savey
                jsr GETIN       ; Get key in acc.
                ldx savex       ; Restore registers.
                ldy savey
                sta pslo,x      ; Push key as lo byte of tos.
                lda #0
                sta pshi,x      ; Clear hi byte of tos.
                dex
                jmp decode      ; Decode next opcode.

;
; Input a line of text.  This routine store the input line always in the same
; location, so calling it multiple times will overwrite the previous input.
; Pushes the address of the input buffer as result.
;
exec_input      stx savex       ; Save registers.
                sty savey
                ldy #0
-               jsr CHRIN       ; Get character from input.
                cmp #13         ; Check for end of input.
                beq +           ; Branch if input is complete.
                iny
                sta INBUF,y     ; Add character to input buffer.
                bne -           ; Get next character.
+               sty INBUF       ; Set length of input buffer.
                ldx savex       ; Restore registers.
                ldy savey
                lda #>INBUF     ; Push address of input buffer
                sta pshi,x
                lda #<INBUF
                sta pslo,x
                dex
                jmp decode      ; Decode next opcode.

;
; Exchange hi and lo bytes of tos.
;
exec_int        inx
                sty savey       ; Save y register in scratch area.
                ldy pshi,x      ; Get hi byte of tos.
                lda pslo,x      ; Get lo byte of tos.
                sta pshi,x      ; Set hi byte of tos.
                tya
                sta pslo,x      ; Set lo byte of tos.
                ldy savey       ; Recover y register from scratch area.
                dex
                jmp decode      ; Decode next opcode.

;
; Compute the remainder after dividing nos by tos and rounding to zero.  The
; remainder will have the same sign as nos.  Drops tos and nos and pushes the
; result.
;
exec_mod        jsr divmod      ; Compute quotient and remainder.
                dex             ; Restore nos.
                lda pshi+1,x    ; Check sign of nos.
                bmi +           ; Branch if nos is negative.
                lda hw          ; Push lo byte of remainder.
                sta pslo+1,x
                lda hw+1        ; Push hi byte of remainder.
                sta pshi+1,x
                jmp decode      ; Decode next opcode.
+               sec
                lda #0          ; Push low byte of negated remainder.
                sbc hw
                sta pslo+1,x
                lda #0          ; Push hi byte of negated remained.
                sbc hw+1
                sta pshi+1,x
                jmp decode      ; Decode next opcode.

;
; Drop tos and multiply nos by tos.
;
exec_mul        lda #0          ; Clear hw.
                sta hw
                sta hw+1
                inx             ; Pop tos to lw.
                lda pslo,x
                sta lw
                lda pshi,x
                sta lw+1
                lda pslo+1,x    ; Copy nos to ea.
                sta ea
                lda pshi+1,x
                sta ea+1
                stx savex       ; Save x register.

                ; Multiplication loop.
                ldx #16         ; Prepare iteration counter.
-               lda lw          ; Test bit 0 of lw.
                lsr
                bcc +           ; Branch if bit is 0.
                clc             ; Add ea to hw if bit is set.
                lda hw
                adc ea
                sta hw
                lda hw+1
                adc ea+1
                sta hw+1
+               lsr hw+1        ; Lsr hw;lw.
                ror hw
                ror lw+1
                ror lw
                dex             ; Next iterations.
                bne -

                ; Finish up.
                ldx savex       ; Restore x register.
                lda lw          ; Push lo byte.
                sta pslo+1,x
                lda lw+1        ; Push hi byte.
                sta pshi+1,x
                jmp decode      ; Decode next opcode.

; to do
exec_new        jmp decode      ; decode next opcode

;
; Increment the current loop index at the top of the return stack.  If it does
; not equal the loop upper bound (second on return stack) then jump to the
; start of the loop (address is third on the return stack).  Otherwise pop the
; current index, upper bound, and loop start address from the return stack.
;
exec_next       stx savex       ; Save param steck pointer.
                tsx             ; Return stack pointer in x register.
                inx
                lda st+2,x      ; Compare upper bound to current index.
                cmp st,x
                beq ++          ; Branch if lo bytes match.
--              inc st,x        ; Upper bound not reached, increment current
                bne +           ; index.
                inc st+1,x
+               lda st+5,x      ; Set program counter to start of for block.
                sta pc+1
                lda st+4,x
                tay
-               ldx savex       ; Restore param stack pointer.
                jmp decode      ; Decode next opcode.
++              lda st+3,x      ; Compare hi bytes of upper bound and
                cmp st+1,x      ; current index+1.
                bne --          ; Branch if upper bound not reached.
                txa             ; Drop current index, upper bound, and loop
                adc #4          ; start address from return stack.  Note that
                tax             ; carry is set before the addition.
                txs
                bne -           ; Branch always (return stack is not full).

;
; Negate tos (flip all its bits).
;
exec_not        inx
                lda pslo,x      ; Bitwise negate tos.
                eor #$ff
                sta pslo,x
                lda pshi,x
                eor #$ff
                sta pshi,x
                dex
                jmp decode      ; Decode next opcode.

;
; Pop tos and logical or it with nos.
;
exec_or         inx
                lda pslo+1,x    ; Logical or low bytes of tos and nos.
                ora pslo,x  
                sta pslo+1,x
                lda pshi+1,x
                ora pshi,x
                sta pshi+1,x
                jmp decode      ; Decode next opcode.

;
; Push nos.
;
exec_over       lda pslo+2,x    ; Push hi byte of nos.
                sta pslo,x
                lda pshi+2,x    ; Push lo byte of nos.
                sta pshi,x
                dex
                jmp decode      ; Decode next opcode.

;
; Pop tos and push unsigned byte (extended to word) at address provided in tos.
;
exec_peek       inx
                lda pslo,x      ; Copy tos to ea.
                sta ea
                lda pshi,x
                sta ea+1
                sty savey       ; Save y register.
                ldy #0          ; Copy (ea) to lo byte of tos
                lda (ea),y
                sta pslo,x
                tya             ; Clear hi byte of tos
                sta pshi,x
                ldy savey       ; Restore y register.
                dex
                jmp decode      ; Decode next opcode.

;
; Interpret tos as 0-based index of the parameter stack and replace tos by the
; word at that index.
;
exec_pick       inx
                stx savex       ; Save param stack pointer for arithmetic.
                lda pslo,x      ; Get stack index from tos.
                clc             ; Add index to param stack pointer
                adc savex
                sty savey       ; Save y register.
                tay             ; Copy lo byte at index to tos.
                lda pslo,y
                sta pslo,x
                lda pshi,y      ; Copy hi byte to tos.
                sta pshi,x
                ldy savey       ; Restore y register.
                dex
                jmp decode      ; Decode next opcode.

;
; Store low byte of nos at address indicated by tos.  Drop tos and no.
;
exec_poke       inx             ; Copy tos into ea
                lda pslo,x
                sta ea
                lda pshi,x
                sta ea+1
                inx             ; Copy lo byte of nos to (ea)
                lda pslo,x
                sty savey       ; Save y register.
                ldy #0
                sta (ea),y
                ldy savey       ; Restore y register.
                jmp decode      ; Decode next opcode.

;
; Print string pointed to by tos and drop tos.  The first byte of the string is
; its unsigned length.  The string content follows after that.
;
exec_print      inx             ; Pop tos into ea.
                lda pslo,x
                sta ea
                lda pshi,x
                sta ea+1
                sty savey       ; Save y register.
                ldy #0          ; Get string length.
                lda (ea),y
                beq +           ; Exit if string is empty.
                stx savex       ; Save x register.
                tax             ; Use x register as character counter.
-               iny             ; Print next character of string.
                lda (ea),y
                jsr CHROUT
                dex             ; Repeat for all characters.
                bne -
                ldx savex       ; Restore x register.
+               ldy savey       ; Restore y register.
                jmp decode      ; Decode next opcode.

;
; Pull address-1 from return stack an continue byte code interpretation at
; address.
;
exec_return     pla             ; Pull lo byte in y register.
                tay
                pla             ; Pull hi byte into pc.
                sta pc+1
                jmp decodenext  ; Decode next opcode.

;
; Generate a pseudo random word using the sequence of steps below to mix a
; three byte random state.  This will loop through all possible non-zero states
; in a random (for our purpose at least) order.  The five steps are:
;
;   Step 1:  rnd[1] <- rnd[1] EOR ASL(rnd[0])
;   Step 2:  rnd[2] <- rnd[2] EOR ROL(rnd[1])
;   Step 3:  rnd[0] <- rnd[0] EOR rnd[2]
;   Step 4:  rnd[2] <- rnd[2] EOR ROR(rnd[1])
;   Step 5:  rnd[1] <- rnd[1] EOR rnd[2]
;

exec_rnd        lda rnd         ; Step 1.
                asl
                eor rnd+1
                sta rnd+1
                rol             ; Step 2.
                eor rnd+2
                sta rnd+2
                eor rnd         ; Step 3.
                sta rnd
                eor #$80        ; Flip bit7 and push as lo byte of result.
                sta pslo,x      ; This makes the value $8000 occur slightly
                                ; less than all others.
                lda rnd+1       ; step 4.
                ror
                eor rnd+2
                sta rnd+2
                eor rnd+1       ; step 5.
                sta rnd+1
                sta pshi,x      ; Push as hi byte of result.
                dex
                jmp decode      ; Decode next opcode.

;
; Interpret tos as a 0-based index into the parameter stack.  Copy the indexed
; word to tos and then remove it from the stack.  The high byte of tos is
; ignored.
;
exec_roll       inx             ; Store param stack pointer for arithmetic.
                stx savex
                lda pslo,x      ; Get stack offset from tos.
                cmp #2          ; Skip roll if offset is less than two.
                bcc +
                clc
                adc savex       ; Add to param stack pointer.
                sty savey       ; Save y register.
                tay             ; Target stack pointer in y register.
                lda pslo,y      ; Copy target register into tos.
                sta pslo,x
                lda pshi,y
                sta pshi,x
-               dey             ; Move adjacent register into target.
                lda pslo,y
                sta pslo+1,y
                lda pshi,y
                sta pshi+1,y
                cpy savex       ; Repeat until tos is moved into nos.
                bne -
                ldy savey       ; Restore y register.
+               jmp decode      ; Decode next opcode.

;
; Store nos as word at addres indicated by tos.  Drop tos and nos.
;
exec_store      inx             ; Pop tos and store into ea.
                lda pslo,x
                sta ea
                lda pshi,x
                sta ea+1
                inx             ; Store lo byte of nos at ea.
                lda pslo,x
                sty savey       ; Save y register.
                ldy #0
                sta (ea),y
                lda pshi,x      ; Store hi byte at ea.
                iny
                sta (ea),y
                ldy savey       ; Restore y register.
                jmp decode      ; Decode next opcode.


;
; Helper routine to output a non-zero binary coded decimal byte to the buffer
; starting at INBUF+1.  Skip possible leading zero in hi nibble.  Byte to write
; in a, string length in y.  Clobbers x.
;
wrt_bcd         tax             ; Save a to x.
                lsr             ; Shift hi nibble down.
                lsr
                lsr
                lsr
                bne +           ; Check for leading zero.
                cpy #0
                beq ++          ; Branch to skip leading zero.
+               ora #'0'        ; Convert to ASCII and add to output.
                sta INBUF+1,y
                iny
++              txa             ; Restore a from x.
wrt_bcd_lo      and #$f         ; Mask out hi nibble.
                ora #'0'        ; Convert to ASCII.
                sta INBUF+1,y   ; Store in buffer.
                iny             ; Increment buffer offset.
wrt_done        rts


;
; Convert signed word in tos to string.  Drop tos and push address of result.
;
exec_str        lda #0          ; Clear binary coded decimal value.
                sta lw
                sta lw+1
                sta hw
                inx             ; Copy tos to ea.
                lda pslo,x
                sta ea
                lda pshi,x
                sta ea+1
                bpl +           ; Branch if tos is non-negative.
                sec             ; Negate ea.
                lda #0
                sbc ea
                sta ea
                lda #0
                sbc ea+1
                sta ea+1
+               sty savey       ; Save y register
                sed             ; Enable decimal arithmetic.

                ; Check if number is zero or at most $ff.
                bne +           ; Branch if hi byte is non-zero.
                lda ea
                bne ++          ; Branch if lo byte is non-zero.
                cld             ; Otherwise skip conversion and output '0'.
                lda #'0'
                sta INBUF+1
                ldy #1          ; String length in y.
                bne push_str    ; Branch always.

                ; Loop over bit15 - bit8.  The maximal decimal value that can
                ; be reached is 128.  The third decimal digit is determined by
                ; the last iteration only.
+               ldy #8
-               asl ea+1        ; Shift next highest bit into the carry.
                lda lw          ; Double the decimal value and add carry.
                adc lw
                sta lw
                dey
                bne -           ; Repeat for all bits of hi byte.
                rol lw+1        ; Carry holds the third decimal digit.

                ; Loop over bit7 - bit1.  The maximal decimal value that can be
                ; reached is 16384.  The fifth decimal digit is determined by
                ; the last iteration only.
++              ldy #7
-               asl ea          ; Shift the next highest bit into the carry.
                lda lw          ; Double the decimal value and add carry.
                adc lw
                sta lw
                lda lw+1
                adc lw+1
                sta lw+1
                dey
                bne -           ; Repeat for seven most significant bits.
                rol hw          ; Carry holds the fifth decimal digit.

                ; Handle bit0
                asl ea
                lda lw
                adc lw
                sta lw
                lda lw+1
                adc lw+1
                sta lw+1
                lda hw
                adc hw
                sta hw

                ; Binary coded decimal now in hw;lw
                cld             ; Disable decimal arithmetic.
                ldy #0          ; Initialize String length counter.
                lda pshi,x      ; Output sign if negative.
                bpl +
                lda #'-'
                sta INBUF+1
                iny
+               stx savex       ; Save x register.
                lda hw          ; Output decimal digits but skip leading 0's.
                bne outdig5
                lda lw+1
                bne outdig34
                beq outdig12    ; Branch alwys.
outdig5         jsr wrt_bcd_lo
                lda lw+1
outdig34        jsr wrt_bcd
outdig12        lda lw
                jsr wrt_bcd
                ldx savex       ; Restore x register.
push_str        sty INBUF       ; Set string length.
                ldy savey       ; Restore y register.
                lda #<INBUF     ; Push address of string.
                sta pslo,x
                lda #>INBUF
                sta pshi,x
                dex
                jmp decode      ; Decode next opcode.

;
; Drop tos and subtract it from nos.
;
exec_sub        sec
                inx
                lda pslo+1,x    ; Subtract lo bytes.
                sbc pslo,x
                sta pslo+1,x
                lda pshi+1,x    ; Subtract hi bytes.
                sbc pshi,x
                sta pshi+1,x
                jmp decode      ; Decode next opcode.

;
; Exchange tos and nos.
;
exec_swap       inx
                sty savey       ; Save y register.
                ldy pslo+1,x    ; Swap lo bytes.
                lda pslo,x
                sta pslo+1,x
                tya
                sta pslo,x
                ldy pshi+1,x    ; Swap hi bytes.
                lda pshi,x
                sta pshi+1,x
                tya
                sta pshi,x
                ldy savey       ; Restore y register.
                dex
                jmp decode      ; Decode next opcode.

;
; Execute external subroutine at address provided by tos.  Drop tos.
;
exec_sys        inx             ; Move tos into ea.
                lda pslo,x
                sta ea
                lda pshi,x
                sta ea+1
                stx savex       ; Save registers since these might get
                sty savey       ; clobbered by the called routine.
!ifdef SYS {
                jsr SYS         ; Execute BASIC SYS command.
} else {
                lda #>(sysr-1)  ; Prepare return address on stack..
                pha
                lda #<(sysr-1)
                pha
                jmp (ea)        ; Jump to specified address.
!address sysr = *
}
                ldx savex       ; Restore registers.
                ldy savey
                jmp decode      ; Decode next opcode.
