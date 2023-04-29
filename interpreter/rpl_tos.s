
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

; Use ea also for tos
!address tos = ea

; Alias for the jmp indirect instruction.
jmpi = $6c

; Hardware stack page.
!address st = $100

;
; Some macros for often recurring code blocks.
;

!macro pushtos {
            lda tos         ; Push tos register onto parameter stack.
            sta pslo,x
            lda tos+1
            sta pshi,x
            dex
}

!macro poptos {
            inx             ; Pup tos register from parameter stack.
            lda pslo,x
            sta tos
            lda pshi,x
            sta tos+1
}

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
push        sta savey       ; Save acc.
            +pushtos        ; Push tos onto parameter stack.
            lda savey       ; Restore acc.
            cmp #$80        ; Check if it is a 15-bit word.
            bcc push15      ; If so then handle it as such.

;
; Push 6-bit signed word.  The opcode has the form %10aa_bbbb and encodes the
; signed 6 bit word aa_bbbb.
;
            cmp #$a0        ; Check sign of 6-bit word.
            bcs +           ; Branch if negative.
            and #$3f        ; Keep the numeric part.
            sta tos         ; Place value in tos.
            lda #0
            sta tos+1
            beq decode      ; Decode next opcode.
+           ora #$c0        ; Sign extend negative word.
            sta tos         ; Place value in tos.
            lda #$ff
            sta tos+1
            bne decode      ; Decode next opcode.

;
; Push 15-bit signed word.  The opcode and its single byte parameter have the
; form %0aaa_bbbb %cccc_dddd and together encode the signed 15 bit word
; aaa_bbbb_cccc_dddd.
;
push15      cmp #$40        ; Check sign.
            bcc +           ; Branch if positive.
            ora #$80        ; Sign extend word.
+           sta tos+1       ; Place value in tos.
            lda (pc),y
            sta tos
            jmp decodenext  ; Decode next opcode.

;
; Push absolute word.  The two byte parameter encodes the word in big endian.
;
; Effect: ( - b )
;
exec_pusha      +pushtos        ; Push tos onto parameter stack.
                lda (pc),y      ; fetch hi byte of word
                sta tos+1       ; push hi byte
                iny             ; increment pc
                beq +           ; handle page boundary
-               lda (pc),y      ; push lo byte
                sta tos
                jmp decodenext  ; decode next opcode
+               inc pc+1
                bne -
;
; Push backward relative word.  Pushes the word address-offset where address is
; the address of the opcode and offset is encoded as an unsigned single byte
; parameter.
;
; Effect: ( - b )
;
exec_pushn      +pushtos        ; Push tos onto parameter stack.
                tya             ; Subtract argument+1 from pc.
                clc
                sbc (pc),y
                sta tos         ; Push lo byte.
                lda pc+1        ; Push hi byte.
                sbc #0
                sta tos+1
                jmp decodenext  ; Decode next opcode.

;
; Push forward relative word.  Pushes the word address+2+offset where address
; is the address of the opcode and offset is encoded as an unsigned single byte
; parameter.
;
; Effect: ( - b )
;
exec_pushp      +pushtos        ; Push tos onto parameter stack.
                tya             ; Add argument+1 to pc.
                sec
                adc (pc),y
                sta tos         ; Push lo byte.
                lda pc+1        ; push hi byte
                adc #0
                sta tos+1
                jmp decodenext  ; Decode next opcode.

;
; Pop tos and nos and push their sum.
;
; Effect: ( a1 a2 - b )
;
exec_add        inx
                clc
                lda tos
                adc pslo,x      ; Add lo bytes of nos and tos.
                sta tos         ; Store as lo byte of nos.
                lda tos+1
                adc pshi,x      ; Add hi bytes of nos and tos.
                sta tos+1       ; Store as hi byte of tos.
                jmp decode      ; Decode next opcode.

;
; Pop tos and nos and push (tos AND nos).
;
; Effect: ( a1 a2 - b )
;
exec_and        inx
                lda tos
                and pslo,x      ; Logical and of lo bytes of nos and tos.
                sta tos         ; Store as lo byte of nos.
                lda tos+1
                and pshi,x      ; Logical and of hi bytes of nos and tos.
                sta tos+1       ; Store as hi byte of nos.
                jmp decode      ; Decode next opcode.

;
; Pop tos and test if it is zero.  Result in z flag.
;
iszero          lda tos         ; Check if tos is zero.  Result in z flag.
                ora tos+1
                sta savey       ; Store result to restore z flag below.
                +poptos         ; Pop tos from parameter stack.
                lda savey       ; Restore z flag.
                rts

;
; Push next-1 on return stack, pop tos and set it as pc.  Here next is the
; address of the next opcode.
;
; Effect: ( a - )
;
exec_gosub      tya             ; Push pc-1 as return address.
                sec
                sbc #1
                sta savey       ; Save low byte to push later.
                lda pc+1
                sbc #0
                pha             ; Push high byte first.
                lda savey       ; Then push low byte.
                pha
                jmp exec_goto   ; Goto address on parameter stack.

;
; Push next-1 on return stack and set pc to target.  Here next is the address
; of the next opcode and target is encoded as a two byte big endian parameter.
;
; Effect: ( - )
;
exec_gosuba     tya             ; Push pc+1 as return address.
                clc
                adc #1
                sta savey       ; Save low byte to push later.
                lda pc+1
                adc #0
                pha             ; Push high byte first.
                lda savey       ; Then push low byte.
                pha
                jmp exec_gotoa  ; Goto address.

;
; Push next-1 on return stack and set pc to target.  Here next is the address
; of the next opcode and target is next-2-offset where offset is encoded as an
; unsigned single byte parameter.
;
; Effect: ( - )
;
exec_gosubn     lda pc+1        ; Push pc as return address.
                pha
                tya
                pha
                jmp exec_goton  ; Goto backward relative address.

;
; Push next-1 on return stack and set pc to target.  Here next is the address
; of the next opcode and target is next+offset where offset is encoded as an
; unsigned single byte parameter.
;
; Effect: ( - )
;
exec_gosubp     lda pc+1        ; Push pc as return address.
                pha
                tya
                pha
                jmp exec_gotop  ; Goto forward relative address.

;
; Pop tos and set it as pc.
;
; Effect: ( a - )
;
exec_goto       lda tos         ; Copy tos to pc.
                tay
                lda tos+1
                sta pc+1
                +poptos         ; Pop tos from parameter stack.
                jmp decode      ; Decode next opcode.

;
; Set pc to address encoded as big endian word parameter.
;
; Effect: ( - )
;
exec_gotoa      lda (pc),y      ; Get hi byte.
                sta savey       ; Save hi byte (pc cannot be adjusted yet).
                iny             ; Increment pc.
                beq +           ; Handle page boundary.
-               lda (pc),y      ; Get lo byte.
                tay             ; Set pc offset.
                lda savey       ; Get hi byte.
                sta pc+1        ; Set hi byte of pc.
                jmp decode      ; Decode next opcode.
+               inc pc+1
                bne -

;
; Set pc to address-offset where address is the address of the opcode and
; offset is encoded as an unsigned single byte parameter.
;
; Effect: ( - )
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
; Effect: ( - )
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
; Effect: ( a - )
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
; Effect: ( a - )
;
exec_beqn       jsr iszero      ; Test and pop tos.
                beq exec_goton  ; Goto backward relative address if zero.
                jmp decodenext  ; Skip operand and decode next opcode.

;
; Pop tos and branch to target if it is zero.  Target equals address+2+offset
; where address is the address of the opcode and offset is encoded as an
; unsigned single byte parameter.
;
; Effect: ( a - )
;
exec_beqp       jsr iszero      ; Test and pop tos.
                beq exec_gotop  ; Goto forward relative address if zero.
                jmp decodenext  ; Skip operand and decode next opcode.

;
; Pop tos and branch to target if it is non-zero.  Target is encoded as a two
; byte big endian parameter.
;
; Effect: ( a - )
;
exec_bnea       jsr iszero      ; Test and pop tos.
                bne exec_gotoa  ; Goto address if not zero.
                beq skip_hi     ; Skip operand and decode next opcode.

;
; Pop tos and branch to target if it is non-zero.  Target equals address-offset
; where address is the address of the opcode and offset is encoded as an
; unsigned single byte parameter.
;
; Effect: ( a - )
;
exec_bnen       jsr iszero      ; Test and pop tos.
                bne exec_goton  ; Goto backward relative address if not zero.
                jmp decodenext  ; Skip operand and decode next opcode.

;
; Pop tos and branch to target if it is non-zero.  Target equals
; address+2+offset where address is the address of the opcode and offset is
; encoded as an unsigned single byte parameter.
;
; Effect: ( a - )
;
exec_bnep       jsr iszero      ; Test and pop tos.
                bne exec_gotop  ; Goto forward relative address if not zero.
                jmp decodenext  ; Skip operand and decode next opcode.

;
; Inspect and drop tos.  Return from subroutine if equal to zero.
;
; Effect: ( a - )
;
exec_req        jsr iszero      ; Test and pop tos.
                beq exec_return ; Return if zero.
                jmp decode      ; Otherwise decode next opcode.

;
; Inspect and drop tos.  Return from subroutine if not equal to zero..
;
; Effect: ( a - )
;
exec_rne        jsr iszero      ; Test and pop tos.
                bne exec_return ; Return if not zero.
                jmp decode      ; Otherwise decode next opcode.

;
; Pull address-1 from return stack an continue byte code interpretation at
; address.
;
; Effect: ( - )
;
exec_return     pla             ; Pull lo byte in y register.
                tay
                pla             ; Pull hi byte into pc.
                sta pc+1
                jmp decodenext  ; Decode next opcode.

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
; Effect: ( a - b )
;
exec_chr        sty savey       ; Save y register.
                ldy tos+1       ; Convert hi byte to hex an add two characters
                jsr hi_ascii    ; to the input buffer.
                sta INBUF+1
                jsr lo_ascii
                sta INBUF+2
                ldy tos         ; Convert lo byte to hex an add two characters
                jsr hi_ascii    ; to the input buffer.
                sta INBUF+3
                jsr lo_ascii
                sta INBUF+4
                ldy savey       ; Restore y register
                lda #4          ; Set string length.
                sta INBUF
                lda #>INBUF     ; Overwrite tos with address of string.
                sta tos+1
                lda #<INBUF
                sta tos
                jmp decode      ; Decode next opcode.

;
; Pop current index, upper bound, and address of for block from the return
; stack.
;
; Effect: ( - )
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
; The remainder is never negative.  Pops nos, saves and clobbers the y
; register.  Keeps the denominator in tos.  The quotient and remainder are left
; in lw and hw respectively.
;
divmod          inx             ; Store numerator in lw.
                lda pslo,x
                sta lw
                lda pshi,x
                sta lw+1
                sta pslo,x      ; Sign of numerator is stored in lo byte.
                lda tos+1       ; Check sign of denominator.
                bpl +           ; Branch if non-negative.
                eor lw+1        ; Store sign of quotient in lo byte of nos.
                sta pslo,x
                sec             ; Negate denominator in tos.
                lda #0
                sbc tos
                sta tos
                lda #0
                sbc tos+1
                sta tos+1
+               lda lw+1        ; Check sign of numerator.
                bpl +           ; Branch if non-negative.
                clc             ; Compute denominator - numerator - 1 in lw.
                lda tos
                sbc lw
                sta lw
                lda tos+1
                sbc lw+1
                sta lw+1
+               lda #0          ; Clear hw.
                sta hw
                sta hw+1
                stx savex       ; Save registers.
                sty savey

                ; Division loop.
                ldx #17         ; Loop counter.
-               rol lw          ; shift hw;lw and shift quotient bit in.
                rol lw+1
                dex             ; Only the first 16 iterations contribute to
                beq +           ; the quotient computation.
                rol hw
                rol hw+1
                sec             ; Compute hw-tos and store in a;y.
                lda hw
                sbc tos
                tay
                lda hw+1
                sbc tos+1
                bcc -           ; Next iteration if tos > hw.
                sty hw          ; Store difference in hw.
                sta hw+1
                bcs -           ; Branch to next iteration.

                ; Finish up.
+               ldx savex       ; Restore x register.  Caller must restore y
                                ; register.
                rts

;
; Return sign fixed remainder in a;y.
;
fixr            lda pshi,x      ; Check sign of numerator.
                bmi +           ; Branch if negative.
                ldy hw          ; Load remainder in a;y.
                lda hw+1
                rts
+               clc
                lda tos         ; Load abs(denominator).
                sbc hw          ; Subtract remainder + 1.
                tay             ; Result in a;y.
                sta hw          ; Store copy of lo byte in hw.
                lda tos+1
                sbc hw+1
+               rts

;
; Return sign fixed quotient in a;y.
;
fixq            lda pslo,x      ; Check sign of quotient.
                bmi +           ; Branch if negative.
                ldy lw          ; Load quotient in a;y.
                lda lw+1
                rts
+               sec             ; Negate quotient and load in a;y.
                lda #0
                sbc lw
                tay
                lda #0
                sbc lw+1
                rts

;
; Compute quotient of nos divided by tos rounded such that the remainder is
; non-negative.  Drop tos and nos and push the result.
;
; Effect: ( a1 a2 - b )
;
exec_div        jsr divmod      ; Compute quotient and remainder.
                jsr fixq        ; Load quotient in a;y.
                sta tos+1       ; Push quotient.
                sty tos
                ldy savey       ; Restore y register.
                jmp decode      ; Decode next opcode.

;
; Compute quotient and remainder of nos divided by tos rounded such that the
; remainder is always non-negative.  Drops tos and nos and pushes the remainder
; and the quotient.
;
; Effect: ( a1 a2 - b1 b2 )
exec_divmod     jsr divmod      ; Compute quotient and remainder.
                jsr fixr        ; Load remainder in a;y.
                sta pshi,x      ; Store hi byte of remainder in nos.  Lo byte
                                ; of nos still holds sign of quotient.
                jsr fixq        ; Load quotient in a;y.
                sta tos+1       ; Store quotient as tos.
                sty tos
                lda hw          ; Now overwrite lo byte of nos with remainder.
                sta pslo,x
                dex             ; Push nos.
                ldy savey       ; Restore y register.
                jmp decode      ; Decode next opcode.

;
; Drop tos.
;
; Effect: ( a - )
;
exec_drop       +poptos         ; Pop tos from parameter stack.
                jmp decode      ; Decode next opcode.

;
; Duplicate tos.
;
; Effect: ( a - b1 b2 )
;
exec_dup        +pushtos        ; Push tos onto parameter stack.
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
+               sta tos         ; Set tos to 0 or -1.
                sta tos+1
                jmp decode      ; Decode next opcode.

;
; Drop tos and nos.  Push -1 (true) if nos <= tos or 0 (false) otherwise.
;
; Effect: ( a1 a2 - b )
;
exec_le         inx
                lda tos         ; Compare tos to nos.
                cmp pslo,x
                lda tos+1
                sbc pshi,x
                jmp binge       ; True if tos greater or equal nos.

;
; Drop tos and nos.  Push -1 (true) if nos < tos or 0 (false) otherwise.
;
; Effect: ( a1 a2 - b )
;
exec_lt         inx
                lda pslo,x      ; Compare nos to tos.
                cmp tos
                lda pshi,x
                sbc tos+1
                jmp binlt       ; True if nos less than tos.

;
; Drop tos and nos.  Push -1 (true) if nos >= tos or 0 (false) otherwise.
;
; Effect: ( a1 a2 - b )
;
exec_ge         inx
                lda pslo,x      ; Compare nos to tos.
                cmp tos
                lda pshi,x
                sbc tos+1
                jmp binge       ; True if nos greater or equal tos.

;
; Drop tos and nos.  Push -1 (true) if nos > tos or 0 (false) otherwise.
;
; Effect: ( a1 a2 - b )
;
exec_gt         inx
                lda tos         ; Compare tos to nos.
                cmp pslo,x
                lda tos+1
                sbc pshi,x
                jmp binlt       ; True if tos less than nos.

;
; Drop tos and nos.  Push -1 (true) if nos == tos or 0 (false) otherwise.
;
; Effect: ( a1 a2 - b )
;
exec_eq         inx
                lda tos         ; Compare lo bytes.
                cmp pslo,x
                bne binfalse    ; False if bytes differ.
                lda tos+1       ; Compare hi bytes.
                cmp pshi,x
                bne binfalse    ; False if bytes differ.
                beq bintrue     ; True if tos equals nos.

;
; Drop tos and nos.  Push -1 (true) if nos != tos or 0 (false) otherwise.
;
; Effect: ( a1 a2 - b )
;
exec_ne         inx
                lda pslo,x      ; Compare lo bytes.
                cmp tos
                bne bintrue     ; True if bytes differ.
                lda pshi,x      ; Compare hi bytes.
                cmp tos+1
                bne bintrue     ; True if bytes differ.
                beq binfalse    ; False if tos equals nos.

;
; Pop tos and push word at address given by tos.
;
; Effect: ( a - b )
;
exec_fetch      stx savex       ; Save registers.
                sty savey
                ldy #0          ; Load word in a;x.
                lda (tos),y
                tax
                iny
                lda (tos),y
                stx tos         ; Store a;x in tos.
                sta tos+1
                ldx savex       ; Restore registers.
                ldy savey
                jmp decode      ; Decode next opcode.

;
; Push current index at top of return stack onto the parameter stack.
;
; Effect: ( - b )
;
exec_fn         +pushtos        ; Push tos onto parameter stack.
                stx savex       ; Save x register.
                tsx             ; Load offset of return stack in x.
                inx
                lda st,x        ; Copy top of return stack into tos.
                sta tos
                lda st+1,x
                sta tos+1
                ldx savex       ; Restore x register.
                jmp decode      ; Decode next opcode.

;
; Push next, nos, and tos on the return stack where next is the address of the
; next opcode.
;
; Effect: ( a1 a2 - )
;
exec_for        lda pc+1        ; Push program counter of the first opcode in.
                pha             ; The for block.
                tya
                pha
                inx             ; Drop nos.
                lda pshi,x      ; Push upper bound of range (nos).
                pha
                lda pslo,x
                pha
                lda tos+1       ; Push current loop index (tos).
                pha
                lda tos
                pha
                +poptos         ; Pop tos from parameter stack.
                jmp decode      ; Decode next opcode.

;
; Get a key from keyboard queue, or 0 if the queue is empty, and push it as an
; unsigned byte.
;
; Effect: ( - b )
;
exec_get        +pushtos        ; Push tos onto parameter stack.
                stx savex       ; Save registers.
                sty savey
                jsr GETIN       ; Get key in acc.
                ldx savex       ; Restore registers.
                ldy savey
                sta tos         ; Push key as lo byte of tos.
                lda #0
                sta tos+1       ; Clear hi byte of tos.
                jmp decode      ; Decode next opcode.

;
; Input a line of text.  This routine store the input line always in the same
; location, so calling it multiple times will overwrite the previous input.
; Pushes the address of the input buffer as result.
;
; Effect: ( - b )
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
                +pushtos        ; Push tos onto parameter stack.
                lda #>INBUF     ; Push address of input buffer
                sta tos+1
                lda #<INBUF
                sta tos
                jmp decode      ; Decode next opcode.

;
; Exchange hi and lo bytes of tos.
;
; Effect: ( a - b )
;
exec_int        sty savey       ; Save y register in scratch area.
                ldy tos+1       ; Get hi byte of tos.
                lda tos         ; Get lo byte of tos.
                sta tos+1       ; Set hi byte of tos.
                sty tos
                ldy savey       ; Recover y register from scratch area.
                jmp decode      ; Decode next opcode.

;
; Compute the remainder after dividing nos by tos rounded such that the
; remainder is always non-negative.  Drop tos and nos and pushes the result.
;
; Effect: ( a1 a2 - b )
;
exec_mod        jsr divmod      ; Compute quotient and remainder.
                jsr fixr        ; Load remainder in a;y.
                sta tos+1       ; Push remainder.
                sty tos
                ldy savey       ; Restore y register.
                jmp decode      ; Decode next opcode.

;
; Drop tos and multiply nos by tos.
;
; Effect: ( a1 a2 - b )
;
exec_mul        lda #0          ; Clear hw.
                sta hw
                sta hw+1
                inx             ; Pop nos to lw.
                lda pslo,x
                sta lw
                lda pshi,x
                sta lw+1
                stx savex       ; Save x register.

                ; Multiplication loop.
                ldx #16         ; Prepare iteration counter.
-               lda lw          ; Test bit 0 of lw.
                lsr
                bcc +           ; Branch if bit is 0.
                clc             ; Add tos to hw if bit is set.
                lda hw
                adc tos
                sta hw
                lda hw+1
                adc tos+1
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
                sta tos
                lda lw+1        ; Push hi byte.
                sta tos+1
                jmp decode      ; Decode next opcode.

; to do
exec_new        jmp decode      ; decode next opcode

;
; Increment the current loop index at the top of the return stack.  If it does
; not equal the loop upper bound (second on return stack) then jump to the
; start of the loop (address is third on the return stack).  Otherwise pop the
; current index, upper bound, and loop start address from the return stack.
;
; Effect: ( - )
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
                ldy st+4,x
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
; Effect: ( a - b )
;
exec_not        lda tos         ; Bitwise negate tos.
                eor #$ff
                sta tos
                lda tos+1
                eor #$ff
                sta tos+1
                jmp decode      ; Decode next opcode.

;
; Multiply nos by two, add to tos, and fetch word.
;
; Effect: ( a1 a2 - b )
;
exec_on         inx
                lda pslo,x      ; Store 2*nos in lw.
                asl
                sta lw
                lda pshi,x
                rol
                sta lw+1
                clc
                lda tos         ; Add tos to tos.
                adc lw
                sta tos
                lda tos+1
                adc lw+1
                sta tos+1
                jmp exec_fetch  ; Fetch word at tos.

;
; Pop tos and logical or it with nos.
;
; Effect: ( a1 a2 - b)
;
exec_or         inx
                lda pslo,x      ; Logical or low bytes of tos and nos.
                ora tos
                sta tos
                lda pshi,x
                ora tos+1
                sta tos+1
                jmp decode      ; Decode next opcode.

;
; Push nos.
;
; Effect: ( a1 a2 - b1 b2 b3 )
;
exec_over       lda tos         ; Push tos to nos.
                sta pslo,x
                lda tos+1
                sta pshi,x
                lda pslo+1,x
                sta tos
                lda pshi+1,x
                sta tos+1
                dex
                jmp decode      ; Decode next opcode.

;
; Pop tos and push unsigned byte (extended to word) at address provided in tos.
;
; Effect: ( a - b )
;
exec_peek       sty savey       ; Save y register.
                ldy #0          ; Fetch byte at tos.
                lda (tos),y
                sta tos         ; Store in tos.
                sty tos+1
                ldy savey       ; Restore y register.
                jmp decode      ; Decode next opcode.

;
; Interpret tos as 0-based index of the parameter stack and replace tos by the
; word at that index.
;
; Effect: ( ... a - ... b )
;
exec_pick       lda tos         ; Ignore hi byte of tos.  If tos is zero then
                beq +           ; this is a no op.
                stx savex       ; Save param stack pointer for arithmetic.
                clc             ; Add tos to param stack pointer.
                adc savex
                tax             ; Copy param stack entry to tos.
                lda pslo,x
                sta tos
                lda pshi,x
                sta tos+1
                ldx savex       ; Restore x register.
+               jmp decode      ; Decode next opcode.

;
; Store low byte of nos at address indicated by tos.  Drop tos and no.
;
; Effect: ( a1 a2 - )
;
exec_poke       inx             ; Load byte from parameter stack.
                lda pslo,x
                sty savey       ; Save y register.
                ldy #0          ; Store byte at tos.
                sta (tos),y
                ldy savey       ; Restore y register.
                +poptos         ; Pop tos from parameter stack.
                jmp decode      ; Decode next opcode.

;
; Print string pointed to by tos and drop tos.  The first byte of the string is
; its unsigned length.  The string content follows after that.
;
; Effect: ( a - )
;
exec_print      sty savey       ; Save y register.
                ldy #0          ; Get string length.
                lda (tos),y
                beq +           ; Exit if string is empty.
                stx savex       ; Save x register.
                tax             ; Use x register as character counter.
-               iny             ; Print next character of string.
                lda (tos),y
                jsr CHROUT
                dex             ; Repeat for all characters.
                bne -
                ldx savex       ; Restore x register.
+               ldy savey       ; Restore y register.
                +poptos         ; Pop tos from parameter stack.
                jmp decode      ; Decode next opcode.

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
; Effect: ( - b )
;
exec_rnd        +pushtos        ; Push tos onto parameter stack.
                lda rnd         ; Step 1.
                asl
                eor rnd+1
                sta rnd+1
                rol             ; Step 2.
                eor rnd+2
                sta rnd+2
                eor rnd         ; Step 3.
                sta rnd
                eor #$80        ; Flip bit7 and store as hi byte of tos.
                sta tos+1       ; This makes the value $8000 occur slightly
                                ; less than all others.
                lda rnd+1       ; step 4.
                ror
                eor rnd+2
                sta rnd+2
                eor rnd+1       ; step 5.
                sta rnd+1
                sta tos         ; Store as lo byte of tos.
                jmp decode      ; Decode next opcode.

;
; Interpret tos as a 0-based index into the parameter stack.  Copy the indexed
; word to tos and then remove it from the stack.  The high byte of tos is
; ignored.
;
; Effect: ( ... a1 a2 - ... b )
;
exec_roll       lda tos         ; Load index, ignore hi byte.
                stx savex       ; Save x register for arithmetic.
                sty savey       ; Save y register.
                tay             ; Use y as count down register.
                clc
                adc savex       ; Add tos to param stack pointer.
                tax
                lda pslo,x      ; Copy target from parameter stack into tos.
                sta tos
                lda pshi,x
                sta tos+1
                dey             ; Move parameter stack entries one position up
                beq +           ; until the count down reaches zero.
-               dex             ; Move parameter stack entries on top of the
                lda pslo,x
                sta pslo+1,x
                lda pshi,x
                sta pshi+1,x
                dey
                bne -
+               ldy savey       ; Restore y register.  The x register is
                                ; already correct at this point.
++              jmp decode      ; Decode next opcode.

;
; Pop element before nos (nnos) from the parameter stack and push it as tos.
;
; Effect: ( a1 a2 a3 - b1 b2 b3 )
;
exec_rot        inx
                sty savey       ; Save y register.
                ldy pslo+1,x    ; Rotate lo bytes.
                lda pslo,x
                sta pslo+1,x
                lda tos
                sta pslo,x
                sty tos
                ldy pshi+1,x    ; Rotate hi bytes.
                lda pshi,x
                sta pshi+1,x
                lda tos+1
                sta pshi,x
                sty tos+1
                ldy savey       ; Restore y register.
                dex
                jmp decode      ; Decode next opcode.

;
; Store nos as word at addres indicated by tos.  Drop tos and nos.
;
; Effect: ( a1 a2 - )
;
exec_store      inx             ; Pop nos and store in address in tos.
                lda pslo,x
                sty savey       ; Save y register.
                ldy #0
                sta (tos),y
                lda pshi,x
                iny
                sta (tos),y
                ldy savey       ; Restore y register.
                +poptos         ; Pop tos from parameter stack.
                jmp decode      ; Decode next opcode.

;
; Convert signed word in tos to string.  Drop tos and push address of result.
;   lw       : Next digit (0 - 9).
;   lw+1     : Leading zero flag.  Bit 7 high means leading zero.
;
; Effect: ( a - b )
;
exec_str        stx savex       ; Save x register.
                sty savey       ; Save y register.
                lda tos+1       ; Check sign of tos.
                bpl +           ; Branch if tos is non-negative.
                sec             ; Negate tos to make it positive.
                lda #0
                sbc tos
                sta tos
                lda #0
                sbc tos+1
                sta tos+1
                lda #'-'        ; Output minus sign.
                sta INBUF+1
                ldx #1          ; Set initial result string length.
                bne ++          ; Branch always.
+               ldx #0          ; Empty result string.
++              lda #$80        ; Set leading zero flag.
                sta lw+1

                ; Digit loop.
                ldy #3          ; Index in power of ten table.
--              lda #0          ; Initialize next digit.
                sta lw

                ; Reduce loop.  Subtract power of 10 while possible.
                lda tos         ; Compare remainder with power of 10.
-               cmp pow10lo,y
                lda tos+1
                sbc pow10hi,y
                bcc +           ; Branch if smaller.
                sta tos+1       ; Subtract power of 10 from remainder.
                lda tos
                sbc pow10lo,y
                sta tos
                inc lw          ; Increment digit.
                bne -           ; Branch always.

                ; Check for leading zero.
+               lda lw          ; Check digit.
                bne +           ; Output if it is non-zero.
                bit lw+1        ; Otherwise check leading zero flag.
                bmi ++          ; Skip digit if it is a leading zero.

                ; Output digit.
+               sta lw+1        ; Reset leading zero flag (digit < $80).
                ora #'0'        ; Output ASCII digit.
                inx
                sta INBUF,x

                ; Next lower power of ten iteration.
++              dey
                bpl --

                ; Output last digit (remainder in hw) and set string length.
                lda tos
                ora #'0'
                inx
                sta INBUF,x
                stx INBUF

                ; Push result.
                ldy savey       ; Restore y register.
                ldx savex       ; Restore x register.
                lda #<INBUF     ; Push INBUF as address of string result.
                sta tos
                lda #>INBUF
                sta tos+1
                jmp decode      ; Decode next opcode.

pow10lo         !byte <10, <100, <1000, <10000
pow10hi         !byte >10, >100, >1000, >10000

;
; Drop tos and subtract it from nos.
;
; Effect: ( a1 a2 - b )
;
exec_sub        inx
                sec
                lda pslo,x      ; Subtract lo bytes.
                sbc tos
                sta tos
                lda pshi,x      ; Subtract hi bytes.
                sbc tos+1
                sta tos+1
                jmp decode      ; Decode next opcode.

;
; Exchange tos and nos.
;
; Effect: ( a1 a2 - b1 b2 )
;
exec_swap       inx
                sty savey       ; Save y register.
                ldy pslo,x      ; Swap lo bytes.
                lda tos
                sta pslo,x
                sty tos
                ldy pshi,x      ; Swap hi bytes.
                lda tos+1
                sta pshi,x
                sty tos+1
                ldy savey       ; Restore y register.
                dex
                jmp decode      ; Decode next opcode.

;
; Execute external subroutine at address provided by tos.  Drop tos.
;
; Effect: ( a - )
;
exec_sys        stx savex       ; Save registers since these might get
                sty savey       ; clobbered by the called routine.
!ifdef SYS {
                jsr SYS         ; Execute BASIC SYS command.
} else {
                lda #>(sysr-1)  ; Prepare return address on stack..
                pha
                lda #<(sysr-1)
                pha
                jmp (tos)       ; Jump to specified address.
!address sysr = *
}
                ldx savex       ; Restore registers.
                ldy savey
                +poptos         ; Pop tos from parameter stack.
                jmp decode      ; Decode next opcode.

;
; Pop tos and nos and push (tos XOR nos).
;
; Effect: ( a1 a2 - b )
;
exec_xor        inx
                lda pslo,x
                eor tos         ; Logical xor of lo bytes of nos and tos.
                sta tos         ; Store as lo byte of nos.
                lda pshi,x
                eor tos+1       ; Logical and of hi bytes of nos and tos.
                sta tos+1       ; Store as hi byte of nos.
                jmp decode      ; Decode next opcode.

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
!word exec_chr
!word exec_clr
!word exec_div
!word exec_divmod
!word exec_drop
!word exec_dup
!word exec_eq
!word exec_fetch
!word exec_fn
!word exec_for
!word exec_ge
!word exec_get
!word exec_gosub
!word exec_gosuba
!word exec_gosubn
!word exec_gosubp
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
!word exec_on
!word exec_or
!word exec_over
!word exec_peek
!word exec_pick
!word exec_poke
!word exec_print
!word exec_req
!word exec_return
!word exec_rnd
!word exec_rne
!word exec_roll
!word exec_rot
!word exec_stop
!word exec_store
!word exec_str
!word exec_sub
!word exec_swap
!word exec_sys
!word exec_xor

