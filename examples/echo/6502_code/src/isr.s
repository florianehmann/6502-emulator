.include "mmio.inc"
.export isr

isr:
    lda TERMIN
    sta TERMOUT
    rti
