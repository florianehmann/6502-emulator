.export start

TERMST  = $D000
TERMOUT = $D001
TERMIN  = $D002

.segment "CODE"

msg:    .byte "Hello, World!"
        .byte $0A               ; newline
msg_end:

start:  ldx #0
@loop:  lda msg,X
        sta TERMOUT
        inx
        cpx #msg_end-msg
        bne @loop

; read from terminal
        lda TERMIN
        sta TERMOUT

        brk
