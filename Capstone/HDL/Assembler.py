#!/usr/bin/env python3
"""
Hack assembler (Nand2Tetris project 6) in Python.

Usage:   python assembler.py Prog.asm
Output:  Prog.hack      (one 16-bit binary instruction per line)
         symbols.txt    (extra feature for K mod 3 == 0: every label and
                         variable with its address)
"""
import os
import sys

# ---------------------------------------------------------------- tables
COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}
DEST = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111",
}
JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}


def predefined_symbols():
    table = {f"R{i}": i for i in range(16)}
    table.update({"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
                  "SCREEN": 16384, "KBD": 24576})
    return table


def clean(line):
    """Remove // comments and all whitespace."""
    return line.split("//")[0].replace(" ", "").replace("\t", "").strip()


# ---------------------------------------------------------------- passes
def first_pass(lines):
    """Strip comments/blank lines, record label addresses.
    Returns (instructions, labels)."""
    instructions = []          # cleaned instruction text
    labels = {}                # label -> ROM address
    for raw in lines:
        line = clean(raw)
        if not line:
            continue
        if line.startswith("(") and line.endswith(")"):
            name = line[1:-1]
            labels[name] = len(instructions)   # next real instruction
        else:
            instructions.append(line)
    return instructions, labels


def encode_a(value):
    return format(value, "016b")


def encode_c(line):
    dest, comp, jump = "", line, ""
    if "=" in line:
        dest, comp = line.split("=", 1)
    if ";" in comp:
        comp, jump = comp.split(";", 1)
    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def second_pass(instructions, symbols):
    """Translate each instruction to 16 bits.
    New variables get RAM addresses 16, 17, 18 ...
    Returns (binary_lines, variables)."""
    out = []
    variables = {}
    next_var = 16
    for line in instructions:
        if line.startswith("@"):
            sym = line[1:]
            if sym.isdigit():
                value = int(sym)
            else:
                if sym not in symbols:
                    symbols[sym] = next_var
                    variables[sym] = next_var
                    next_var += 1
                value = symbols[sym]
            out.append(encode_a(value))
        else:
            out.append(encode_c(line))
    return out, variables


def write_symbols(path, labels, variables):
    with open(path, "w") as f:
        f.write("# Labels (ROM addresses)\n")
        for name, addr in labels.items():
            f.write(f"{name}\t{addr}\n")
        f.write("\n# Variables (RAM addresses)\n")
        for name, addr in variables.items():
            f.write(f"{name}\t{addr}\n")


# ---------------------------------------------------------------- main
def assemble(src_path):
    with open(src_path) as f:
        lines = f.read().splitlines()

    instructions, labels = first_pass(lines)
    symbols = predefined_symbols()
    symbols.update(labels)
    binary, variables = second_pass(instructions, symbols)

    base = os.path.splitext(src_path)[0]
    hack_path = base + ".hack"
    with open(hack_path, "w") as f:
        f.write("\n".join(binary) + "\n")

    sym_path = os.path.join(os.path.dirname(os.path.abspath(src_path)), "symbols.txt")
    write_symbols(sym_path, labels, variables)

    print(f"{src_path} -> {hack_path} ({len(binary)} instructions)")
    print(f"symbols  -> {sym_path} ({len(labels)} labels, {len(variables)} variables)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler.py Prog.asm")
        sys.exit(1)
    assemble(sys.argv[1])