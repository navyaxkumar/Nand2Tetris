// Box.asm  --  K = 54
// While ANY key is pressed: draw a black box. Key released: box is erased.
//
// Box: starts at row 54, 20 rows tall (rows 54..73),
//      width = 16 * ((54 mod 4) + 1) = 48 pixels = 3 words, at the left edge.
// Row r starts at SCREEN + 32*r, so the first word is SCREEN + 32*54 = 16384 + 1728.


(LOOP)
    @KBD
    D=M
    @BLACK
    D;JNE

    @color
    M=0
    @DRAW
    0;JMP

(BLACK)
    @color
    M=-1

(DRAW)

    @1728            // 32 * 54
    D=A
    @SCREEN
    D=D+A            // D = address of first word of row 54
    @addr
    M=D
    @20              // number of rows
    D=A
    @rows
    M=D

(ROWLOOP)
    @color
    D=M
    @addr
    A=M
    M=D              // word 0
    A=A+1
    M=D              // word 1
    A=A+1
    M=D              // word 2  (3 words = 48 pixels)

    @32
    D=A
    @addr
    M=D+M            // addr = addr + 32  (next row)

    @rows
    M=M-1
    D=M
    @ROWLOOP
    D;JGT            // more rows left?

    @LOOP
    0;JMP