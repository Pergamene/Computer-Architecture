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
      0b10100000: self.handle_add,
      0b10100010: self.handle_mul,
      0b01000101: self.handle_push,
      0b01000110: self.handle_pop,
      0b01010000: self.handle_call,
      0b00010001: self.handle_ret,
    }

  def load(self, path):
    """Load a program into memory."""
    try:
      address = 0
      with open(path) as program:
        for line in program:
          cmd = line.split('#')[0].strip()
          if cmd != '':
            self.ram[address] = int(cmd, 2)
            address += 1
    except FileNotFoundError:
      print('File not found')
      sys.exit(2)

  def alu(self, op, reg_a, reg_b):
    """ALU operations."""
    if op == "ADD":
      self.reg[reg_a] += self.reg[reg_b]
    elif op == "MUL":
      self.reg[reg_a] *= self.reg[reg_b]
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
      operand_a = self.ram_read(self.pc + 1)
      operand_b = self.ram_read(self.pc + 2)
      operands = ir >> 6
      self.pc += 1 + operands
      if operands == 0:
        self.OP_CODES[ir]()
      elif operands == 1:
        self.OP_CODES[ir](operand_a)
      else:
        self.OP_CODES[ir](operand_a, operand_b)

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

  def handle_add(self, reg_a, reg_b):
    self.alu('ADD', reg_a, reg_b)

  def handle_mul(self, reg_a, reg_b):
    self.alu('MUL', reg_a, reg_b)

  def handle_pop(self, reg_a):
    self.reg[reg_a] = self.ram_read(self.reg[7])
    self.reg[7] += 1

  def handle_push(self, reg_a):
    self.reg[7] -= 1
    self.ram_write(self.reg[reg_a], self.reg[7])

  def handle_call(self, reg_a):
    self.reg[7] -= 1
    self.ram_write(self.pc, self.reg[7])
    self.pc = self.reg[reg_a]

  def handle_ret(self):
    self.pc = self.ram_read(self.reg[7])
    self.reg[7] += 1
