# Nand2Tetris Capstone Project: Make the Computer Draw a Box

**Course:** Nand to Tetris - I (ETCCNT301)
**Student:** Navya Kumar
**Roll Number:** 2501410054
**Project:** Capstone

---

## Project Overview

This project builds a small Hack computer and a Hack assembly program that draws a black box on the screen while a key is pressed. When the key is released, the box is erased.

The work is split into three parts, as set in the capstone brief:

- **Part A - Build the computer:** join the CPU, memory and computer-level chips and check them with the supplied test scripts.
- **Part B - Python assembler:** translate Hack assembly (`.asm`) into 16-bit machine code (`.hack`) in two passes, plus the extra feature chosen by my roll number.
- **Part C - Box program:** write `Box.asm`, assemble it with my own assembler, and run it in the CPU Emulator.

---

## Personal Configuration

K is the last two digits of the roll number.

| Item | Value |
|---|---|
| Roll number | 2501410054 |
| K | 54 |
| Starting screen row | 54 (rows 54 to 73) |
| Box height | 20 rows |
| Box width | 48 pixels |
| Words per screen row | 32 |
| Words used by the box in each row | 3 |
| Extra assembler feature | K mod 3 = 0, so labels and variables are saved with their addresses in `symbols.txt` |

Width = 16 x ((K mod 4) + 1) = 16 x ((54 mod 4) + 1) = 16 x 3 = **48 pixels**.

One screen row is 32 words and each word is 16 pixels. The screen starts at address 16384, so the first word of the box is:

16384 + (32 x 54) = 16384 + 1728 = **18112**

The box covers 3 consecutive words on each of 20 rows, starting at address 18112.

---

## Repository Contents

```
Capstone/
├── HDL/
│   ├── CPU.hdl
│   ├── Memory.hdl
│   └── Computer.hdl
│
├── Tests/
│   ├── CPU.tst           CPU.cmp           
│   ├── Memory.tst        Memory.cmp        
│   ├── ComputerAdd.tst   ComputerAdd.cmp   
│   ├── ComputerMax.tst   ComputerMax.cmp   
│   ├__ ComputerRect.tst  ComputerRect.cmp  
│   
│
├── Assembler/            (test programs for Part B, not the assembler itself)
│   ├── Add.asm    Add.hack
│   ├── Max.asm    Max.hack
│   ├── Rect.asm   Rect.hack
│   └── Pong.asm   Pong.hack
│
├── Box/
│   ├── Assembler.py      (my Python assembler)
│   ├── Box.asm
│   ├── Box.hack
│   └── symbols.txt
│
├── screenshots/
│   ├── CPU_test.png
│   ├── Memory_Test.png
│   ├── Computer_Add.png
│   ├── Computer_Max.png
│   ├── Computer_Rect.png
│   ├── Box.hack_loaded.png
│   ├── Box_key_pressed.png
│   └── Box_key_released.png
│
└── README.md
```

---

## Part A - Building the Hack Computer

The three chips were tested in the Nand2Tetris Hardware Simulator (version 2.5).

### CPU.hdl
Bit 15 of the instruction separates A-instructions (0) from C-instructions (1). The A register loads either the instruction itself (A-instruction) or the ALU output (C-instruction with the A destination bit set). The ALU's second input is A or `inM`, chosen by the `a` bit (bit 12). The D register and `writeM` are controlled by the destination bits (bits 4 and 3). The jump decision combines the three jump bits with the ALU flags `zr` and `ng` (positive means neither flag is set). It is only applied to C-instructions, and it loads the program counter (`PC`) with the address in A.

### Memory.hdl
Address bits 14 and 13 pick the region. A `DMux4Way` routes the `load` signal, and a `Mux4Way16` picks the output.

| Component | Address range | Address bits 14, 13 |
|---|---|---|
| RAM16K | 0 - 16383 | 00 and 01 |
| Screen | 16384 - 24575 | 10 |
| Keyboard | 24576 | 11 |

### Computer.hdl
Connects `ROM32K` (instruction memory), the `CPU` and `Memory`. The CPU's `pc` addresses the ROM, and the CPU's `outM`, `writeM` and `addressM` drive the memory.

### Test results

| Test | Result |
|---|---|
| CPU.tst | Passed |
| Memory.tst | Passed |
| ComputerAdd.tst | Passed |
| ComputerMax.tst | Passed |
| ComputerRect.tst | Passed |

Each run ended with "End of script - Comparison ended successfully". The screenshots are in `screenshots/`, and the `.out` files in `Tests/` hold the saved outputs next to the supplied `.cmp` files.

> The chips used inside these three files (including `ARegister`, `DRegister`, `PC`, `RAM16K`, `Screen`, `Keyboard`, `ROM32K` and the logic gates) are the Hardware Simulator's built-in versions. The Computer test scripts read the internal values of `ARegister`, `DRegister`, `PC` and `RAM16K`, so they only work with the built-in chips.

### Re-running the tests

Copy the three files from `HDL/` and the test files from `Tests/` into one folder, together with `Add.hack`, `Max.hack` and `Rect.hack` from `Assembler/` (the Computer tests load these by name). Then load each `.hdl` in the Hardware Simulator, load the matching `.tst`, and run it.

---

## Part B - Python Hack Assembler

The assembler is `Box/Assembler.py`.

### How it works

1. **Clean:** each line has its `//` comment and all whitespace removed. Blank lines are dropped.
2. **First pass:** the assembler records the ROM address of every label such as `(LOOP)`. Labels do not occupy an instruction address, and a duplicate label raises an error.
3. **Second pass:** every remaining line is translated to 16 bits.
   - `@number` becomes the number in 16-bit binary.
   - `@symbol` is looked up in the symbol table. This holds the predefined symbols (`R0`-`R15`, `SP`, `LCL`, `ARG`, `THIS`, `THAT`, `SCREEN`, `KBD`) and the labels. A symbol not found is a variable and gets the next free RAM address, starting at 16, then 17, 18 and so on.
   - A C-instruction becomes `111` + comp bits + dest bits + jump bits, using lookup tables.
4. The result is written to a `.hack` file beside the input file.

### Extra feature for K = 54 (54 mod 3 = 0)

After assembling, the assembler writes every label (with its ROM address) and every variable (with its RAM address) to `symbols.txt`, in the same folder as the input file.

For `Box.asm` it records:

| Symbol | Kind | Address |
|---|---|---|
| LOOP | label | 0 |
| BLACK | label | 8 |
| DRAW | label | 10 |
| ROWLOOP | label | 20 |
| color | variable | 16 |
| addr | variable | 17 |
| rows | variable | 18 |

### Assembler tests

The assembler was run on the four programs from the brief. Each output was compared with a reference assembler's output, and all four matched exactly.

| Program | Source | Generated machine code | Instructions |
|---|---|---|---|
| Add | Assembler/Add.asm | Assembler/Add.hack | 6 |
| Max | Assembler/Max.asm | Assembler/Max.hack | 16 |
| Rect | Assembler/Rect.asm | Assembler/Rect.hack | 25 |
| Pong | Assembler/Pong.asm | Assembler/Pong.hack | 27483 |

### Running the assembler

Run these from the `Capstone` directory:

```
python Box/Assembler.py Assembler/Add.asm
python Box/Assembler.py Assembler/Max.asm
python Box/Assembler.py Assembler/Rect.asm
python Box/Assembler.py Assembler/Pong.asm
python Box/Assembler.py Box/Box.asm
```

The assembler writes `symbols.txt` next to the file it assembles, so assembling the test programs creates a `symbols.txt` inside `Assembler/`. The one in `Box/` is the one for the box program.

---

## Part C - The Box Program

`Box/Box.asm` is assembled with my own assembler (not the official one) to produce `Box/Box.hack`.

### Program flow

1. **Read the keyboard.** Load `@KBD` into D. A non-zero value means a key is pressed.
2. **Pick the colour.** If a key is pressed, set the variable `color` to -1 (all 16 pixels of a word black). Otherwise set `color` to 0 (white).
3. **Set up.** Set `addr` to 18112 (`SCREEN` + 32 x 54, the first word of row 54) and `rows` to 20.
4. **Draw each row.** Write `color` into three consecutive words (48 pixels), then add 32 to `addr` to reach the same position on the next row. Decrement `rows`.
5. **Repeat.** When `rows` reaches 0, jump back to step 1.

Because the same drawing loop runs with `color` = -1 or 0, the box appears while a key is held and is erased when it is released.

### Running the program

```
python Box/Assembler.py Box/Box.asm
```

Then open the Nand2Tetris CPU Emulator (the web IDE was used for the screenshots), load `Box.hack`, and run it. Hold any key to see the box, and release it to clear the box.

### Screenshots

- `screenshots/Box.hack_loaded.png` - program loaded in the CPU Emulator
- `screenshots/Box_key_pressed.png` - key pressed, black box displayed
- `screenshots/Box_key_released.png` - key released, box cleared

---

## Mistake Encountered and Fixed

While running `ComputerAdd.tst` in the Hardware Simulator, I got the error "no such built-in register PC". The test script prints the internal values of `PC`, `ARegister`, `DRegister` and `RAM16K`, and it can only read them from the simulator's built-in chips. I had copied my own lab `PC.hdl` into the same folder as `Computer.hdl`, so the simulator loaded my hand-built chip instead of the built-in one. I fixed it by moving my own chip files out of the folder, so that only `CPU.hdl`, `Memory.hdl` and `Computer.hdl` remained, and the tests then passed.

---

## Final Project Checklist

| Requirement | Status |
|---|---|
| CPU.hdl, Memory.hdl and Computer.hdl implemented | Completed |
| Five Part A test scripts passed | Completed |
| Python assembler implemented using two passes | Completed |
| Add, Max, Rect and Pong outputs compared | Completed |
| Required symbols.txt feature for K = 54 | Completed |
| Box.asm written for the assigned dimensions | Completed |
| Box.hack generated using my own assembler | Completed |
| Key press and release behaviour tested | Completed |
| Screenshots organised in screenshots/ | Completed |

---

## Conclusion

This capstone brought together the hardware and software sides of the Hack computer. The first part connected the CPU and memory and checked the complete computer against the supplied tests. The second part was a Python assembler with label handling, variable allocation and the symbol-table output required for K = 54. The last part used that assembler to turn a Hack program into machine code that reads the keyboard and draws and clears a 48-by-20-pixel box at the position given by my roll number.

---

## Files in This Directory

- `HDL/` - CPU.hdl, Memory.hdl and Computer.hdl.
- `Tests/` - supplied test scripts and outputs (`.cmp`).
- `Assembler/` - the four test programs for Part B and their machine code.
- `Box/Assembler.py` - the Python assembler.
- `Box/Box.asm`, `Box/Box.hack`, `Box/symbols.txt` - the Part C program, its machine code and its symbol table.
- `screenshots/` - screenshots of the test results and of the box program.