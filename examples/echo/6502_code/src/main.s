.include "mmio.inc"
.export start

.segment "CODE"

msg:    .byte "Hello, World!", $0D
        .byte "This program runs in a 6502 emulator.", $0D
        .byte "Type something and it will be echoed back!", $0D
        .byte "Press Ctrl+C to exit.", $0D
msg_end:

start:
        ldx #0
@loop:  lda msg,X
        sta TERMOUT
        inx
        cpx #msg_end-msg
        bne @loop

wait:   jmp wait
