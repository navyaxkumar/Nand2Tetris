# Nand2Tetris Capstone Project: Make the Computer Draw a Box

**Course:** Nand to Tetris - I (ETCCNT301)
**Student:** Navya Kumar
**Roll Number:** 2501410054
**Personal Number (K):** 54
**Programme:** B.Tech CSE (Cyber Security), Semester 3
**Project:** Capstone

---

## Project Overview

This project builds a small Hack computer and a Hack assembly program that draws a black box on the screen while a key is pressed. When the key is released, the box is erased.

The work is split into three parts, as set in the capstone brief:

- **Part A - Build the computer:** join the CPU, memory and computer-level chips and check them with the official test scripts.
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
| Box width | 48 pixels (3 words) |
| Words per screen row | 32 |
| First screen word of the box | 18112 |
| Extra assembler feature | K mod 3 = 0: save labels and variables with their addresses in `symbols.txt` |

Width = 16 x ((K mod 4) + 1) = 16 x ((54 mod 4) + 1) = 16 x 3 = **48 pixels**.

One screen row is 32 words and each word is 16 pixels. The screen starts at address 16384, so the first word of the box is:

16384 + (32 x 54) = 16384 + 1728 = **18112**

The box covers 3 consecutive words on each of 20 rows, starting at address 18112.

---

## Repository Structure

```
Capstone/
├── Part A/
│   ├── CPU.hdl
│   ├── Memory.hdl
│   ├── Computer.hdl
│   └── screenshots/
│       ├── CPU_test.png
│       ├── Memory_Test.png
│       ├── Computer_Add.png
│       ├── Computer_Max.png
│       └── Computer_Rect.png
│
├── Part B/
│   ├── Assembler.py
│   └── test_programs/
│       ├── Add.asm    Add.hack
│       ├── Max.asm    Max.hack
│       ├── Rect.asm   Rect.hack
│       ├── Pong.asm   Pong.hack
│       └── symbols.txt
│
├── Part C/
│   ├── Box.asm
│   ├── Box.hack
│   ├── symbols.txt
│   └── screenshots/
│       ├── Box.hack_loaded.png
│       ├── Box_key_pressed.png
│       └── Box_key_released.png
│
├── Project Report/
│   └── Nand2Tetris Capstone Report .pdf
│
└── README.md
```

---

## Part A - Building the Hack Computer

**Files:** `Part A/CPU.hdl`, `Part A/Memory.hdl`, `Part A/Computer.hdl`

The three chips were tested in the Nand2Tetris Hardware Simulator (version 2.5) with the official test files `CPU.tst`, `Memory.tst`, `ComputerAdd.tst`, `ComputerMax.tst` and `ComputerRect.tst`.

### CPU.hdl
Bit 15 of the instruction separates A-instructions (0) from C-instructions (1). The A register loads either the instruction itself (A-instruction) or the ALU output (C-instruction with the A destination bit set). The ALU's second input is A or `inM`, chosen by the `a` bit (bit 12). The D register and `writeM` are controlled by the destination bits (bits 4 and 3). The jump decision combines the three jump bits with the ALU flags `zr` and `ng` (positive means neither flag is set). It applies only to C-instructions, and it loads the program counter with the address in A.

### Memory.hdl
Address bits 14 and 13 pick the region. A `DMux4Way` routes the `load` signal and a `Mux4Way16` picks the output.

| Component | Address range | Address bits 14, 13 |
|---|---|---|
| RAM16K | 0 - 16383 | 00 and 01 |
| Screen | 16384 - 24575 | 10 |
| Keyboard | 24576 | 11 |

### Computer.hdl
Connects `ROM32K` (instruction memory), the `CPU` and `Memory`. The CPU's `pc` addresses the ROM, and its `outM`, `writeM` and `addressM` drive the memory.

### Test results

| Test | Result | Screenshot |
|---|---|---|
| CPU.tst | Passed | `Part A/screenshots/CPU_test.png` |
| Memory.tst | Passed | `Part A/screenshots/Memory_Test.png` |
| ComputerAdd.tst | Passed | `Part A/screenshots/Computer_Add.png` |
| ComputerMax.tst | Passed | `Part A/screenshots/Computer_Max.png` |
| ComputerRect.tst | Passed | `Part A/screenshots/Computer_Rect.png` |

Each run ended with "End of script - Comparison ended successfully".

> **Built-in chips:** the chips used inside these three files (`ARegister`, `DRegister`, `PC`, `RAM16K`, `Screen`, `Keyboard`, `ROM32K` and the logic gates) are the simulator's built-in versions. The Computer test scripts read the internal values of `ARegister`, `DRegister`, `PC` and `RAM16K`, so they only work with the built-in chips.

### Re-running the tests

Put `CPU.hdl`, `Memory.hdl` and `Computer.hdl` in one folder with the official `.tst` and `.cmp` files and the programs `Add.hack`, `Max.hack` and `Rect.hack` (from `Part B/test_programs/`). Do not put your own `PC.hdl` or `RAM16K.hdl` there. Load each `.hdl` in the Hardware Simulator, load the matching `.tst`, and run it.

---

## Part B - Python Hack Assembler

**Files:** `Part B/Assembler.py`, `Part B/test_programs/`

### How it works

1. **Clean:** each line has its `//` comment and all whitespace removed. Blank lines are dropped.
2. **First pass:** record the ROM address of every label such as `(LOOP)`. Labels take no instruction address, and a duplicate label raises an error.
3. **Second pass:** translate every remaining line to 16 bits.
   - `@number` becomes the number in 16-bit binary.
   - `@symbol` is looked up in the symbol table (`R0`-`R15`, `SP`, `LCL`, `ARG`, `THIS`, `THAT`, `SCREEN`, `KBD` and the labels). A name not found is a variable and gets the next free RAM address, starting at 16, then 17, 18 and so on.
   - A C-instruction becomes `111` + comp bits + dest bits + jump bits, using lookup tables.
4. **Output:** the `.hack` file is written beside the input file.

### Extra feature for K = 54 (54 mod 3 = 0)

After assembling, the assembler writes every label (with its ROM address) and every variable (with its RAM address) to `symbols.txt`, in the same folder as the input file.

For `Box.asm` (`Part C/symbols.txt`):

| Symbol | Kind | Address |
|---|---|---|
| LOOP | label | 0 |
| BLACK | label | 8 |
| DRAW | label | 10 |
| ROWLOOP | label | 20 |
| color | variable | 16 |
| addr | variable | 17 |
| rows | variable | 18 |

`Part B/test_programs/symbols.txt` is the symbol table of the last test program assembled (`Pong.asm`), because `symbols.txt` is overwritten on each run.

### Assembler tests

The assembler was run on the four programs from the brief and each output was compared with the reference output. All four matched exactly.

| Program | Source | Output | Instructions |
|---|---|---|---|
| Add | `test_programs/Add.asm` | `test_programs/Add.hack` | 6 |
| Max | `test_programs/Max.asm` | `test_programs/Max.hack` | 16 |
| Rect | `test_programs/Rect.asm` | `test_programs/Rect.hack` | 25 |
| Pong | `test_programs/Pong.asm` | `test_programs/Pong.hack` | 27483 |

### Running the assembler

Run these from the `Capstone` directory:

```
python "Part B/Assembler.py" "Part B/test_programs/Add.asm"
python "Part B/Assembler.py" "Part B/test_programs/Max.asm"
python "Part B/Assembler.py" "Part B/test_programs/Rect.asm"
python "Part B/Assembler.py" "Part B/test_programs/Pong.asm"
python "Part B/Assembler.py" "Part C/Box.asm"
```

---

## Part C - The Box Program

**Files:** `Part C/Box.asm`, `Part C/Box.hack`, `Part C/symbols.txt`

`Box.asm` is assembled with my own assembler (not the official one) to produce `Box.hack` (40 instructions).

### Program flow

1. Read the keyboard (`@KBD`). A non-zero value means a key is pressed.
2. Key pressed: set the variable `color` to -1 (all 16 pixels of a word black). No key: set `color` to 0 (white).
3. Set `addr` to 18112 (`SCREEN` + 32 x 54, the first word of row 54) and `rows` to 20.
4. For each row, write `color` into 3 consecutive words (48 pixels), add 32 to `addr` to reach the same position on the next row, and decrement `rows`.
5. When `rows` reaches 0, go back to step 1.

Because the same drawing loop runs with `color` = -1 or 0, the box appears while a key is held and is erased when it is released.

### Running the program

```
python "Part B/Assembler.py" "Part C/Box.asm"
```

Then open the Nand2Tetris CPU Emulator (the web IDE was used for the screenshots), load `Box.hack`, and run it. Hold any key to see the box, and release it to clear the box.

### Screenshots

| Screenshot | Shows |
|---|---|
| `Part C/screenshots/Box.hack_loaded.png` | Program loaded in the CPU Emulator |
| `Part C/screenshots/Box_key_pressed.png` | Key pressed: black box displayed |
| `Part C/screenshots/Box_key_released.png` | Key released: box cleared |

---

## Mistake Encountered and Fixed

While running `ComputerAdd.tst` I got the error "no such built-in register PC". The test script prints the internal values of `PC`, `ARegister`, `DRegister` and `RAM16K`, and it can only read them from the simulator's built-in chips. I had copied my own lab `PC.hdl` into the same folder as `Computer.hdl`, so the simulator loaded my hand-built chip instead of the built-in one. I fixed it by moving my own chip files out of the folder, leaving only `CPU.hdl`, `Memory.hdl` and `Computer.hdl`, and the tests then passed.

---

## Project Report

The submitted report is in `Project Report/Nand2Tetris Capstone Report .pdf`. It contains my name, roll number, K, the box size, the test screenshots, the box screenshots and the mistake paragraph.

---

## Final Project Checklist

| Requirement | Status |
|---|---|
| CPU.hdl, Memory.hdl and Computer.hdl implemented | Completed |
| Five official tests passed, with screenshots | Completed |
| Python assembler implemented using two passes | Completed |
| Add, Max, Rect and Pong outputs compared | Completed |
| Extra feature for K = 54 (`symbols.txt`) | Completed |
| Box.asm written for the assigned dimensions | Completed |
| Box.hack generated using my own assembler | Completed |
| Key press and release behaviour tested, with screenshots | Completed |
| Report with K, box size and mistake paragraph | Completed |

---

## Conclusion

This capstone brought together the hardware and software sides of the Hack computer. The CPU, memory and computer chips pass all five official tests. The Python assembler uses two passes, allocates variables from address 16 and writes the `symbols.txt` required for K = 54. The last part used that assembler to turn a Hack program into machine code that reads the keyboard and draws and clears a 48 x 20 pixel box at row 54.