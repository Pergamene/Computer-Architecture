"""CPU functionality."""

import sys

class CPU:
  """Main CPU class."""

  def __init__(self):
    """Construct a new CPU."""
    self.ram = [0] * 256
    self.reg = [0, 0, 0, 0, 0, 0, 0, 0xf4]
    self.pc = 0
    self.fl = 0

    self.OP_CODES = {
      0b00000001: self.handle_hlt,
      0b10000010: self.handle_ldi,
      0b01000111: self.handle_prn,
    }

  def load(self):
    """Load a program into memory."""
    address = 0
    # For now, we've just hardcoded a program:
    program = [
      # From print8.ls8
      0b10000010, # LDI R0,8
      0b00000000,
      0b00001000,
      0b01000111, # PRN R0
      0b00000000,
      0b00000001, # HLT
    ]
    for instruction in program:
      self.ram[address] = instruction
      address += 1

  def alu(self, op, reg_a, reg_b):
    """ALU operations."""
    if op == "ADD":
      self.reg[reg_a] += self.reg[reg_b]
    #elif op == "SUB": etc
    else:
      raise Exception("Unsupported ALU operation")

  def trace(self):
    """
    Handy function to print out the CPU state. You might want to call this
    from run() if you need help debugging.
    """
    print(f"TRACE: %02X | %02X %02X %02X |" % (
      self.pc,
      #self.fl,
      #self.ie,
      self.ram_read(self.pc),
      self.ram_read(self.pc + 1),
      self.ram_read(self.pc + 2)
    ), end='')
    for i in range(8):
      print(" %02X" % self.reg[i], end='')
    print()

  def run(self):
    """Run the CPU."""
    while True:
      ir = self.ram_read(self.pc)
      operands = ir >> 6
      if operands == 0:
        self.OP_CODES[ir]()
      elif operands == 1:
        self.OP_CODES[ir](self.ram_read(self.pc + 1))
      else:
        self.OP_CODES[ir](self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
      self.pc += 1 + operands

  def ram_read(self, mar):
    """
    Accept the address to read and return the value stored there.
    MAR == Memory Address Register - address that is being read or written to.
    """
    return self.ram[mar]

  def ram_write(self, mdr, mar):
    """
    Accept the value to write, and the address to write it to.
    MDR == Memory Data Register - data that was read or the data to write.
    MAR == Memory Address Register - address that is being read or written to.
    """
    self.ram[mar] = mdr

  def handle_hlt(self):
    sys.exit(0)

  def handle_ldi(self, reg_a, immediate):
    self.reg[reg_a] = immediate

  def handle_prn(self, reg_a):
    print(self.reg[reg_a])
