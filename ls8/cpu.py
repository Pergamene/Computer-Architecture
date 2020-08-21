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
    self.masked_interrupts = 0

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
      0b01010100: self.handle_jmp,
      0b10100111: self.handle_cmp,
      0b01010101: self.handle_jeq,
      0b01010110: self.handle_jne,
      0b10101000: self.handle_and,
      0b10101010: self.handle_or,
      0b10101011: self.handle_xor,
      0b01101001: self.handle_not,
      0b10101100: self.handle_shl,
      0b10101101: self.handle_shr,
      0b10100100: self.handle_mod,
      0b01100110: self.handle_dec,
      0b10100011: self.handle_div,
      0b01100101: self.handle_inc,
      0b01010010: self.handle_int,
      0b00010011: self.handle_iret,
      0b01011010: self.handle_jge,
      0b01010111: self.handle_jgt,
      0b01011001: self.handle_jle,
      0b01011000: self.handle_jlt,
      0b10000011: self.handle_ld,
      0b00000000: self.handle_nop,
      0b01001000: self.handle_pra,
      0b10000100: self.handle_st,
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
    if op == 'ADD':
      self.reg[reg_a] += self.reg[reg_b] & 0xff
    elif op == 'MUL':
      self.reg[reg_a] *= self.reg[reg_b] & 0xff
    elif op == 'CMP':
      res = self.reg[reg_a] - self.reg[reg_b]
      if res < 0:
        self.fl = 0b00000100
      elif res > 0:
        self.fl = 0b00000010
      else:
        self.fl = 0b00000001
    elif op == 'AND':
      self.reg[reg_a] &= self.reg[reg_b]
    elif op == 'OR':
      self.reg[reg_a] |= self.reg[reg_b]
    elif op == 'XOR':
      self.reg[reg_a] ^= self.reg[reg_b]
    elif op == 'NOT':
      self.reg[reg_a] = ~self.reg[reg_a]
    elif op == 'SHL':
      self.reg[reg_a] <<= self.reg[reg_b]
    elif op == 'SHR':
      self.reg[reg_b] >>= self.reg[reg_b]
    elif op == 'MOD':
      if self.reg[reg_b] == 0:
        print('You can not divid by 0')
        self.handle_hlt()
      self.reg[reg_a] %= self.reg[reg_b] & 0xff
    elif op == 'DEC':
      self.reg[reg_a] -= 1 & 0xff
    elif op == 'DIV':
      if self.reg[reg_b] == 0:
        print('You can not divid by 0')
        self.handle_hlt()
      self.reg[reg_a] /= self.reg[reg_b] & 0xff
    elif op == 'INC':
      self.reg[reg_a] += 1 & 0xff
    else:
      raise Exception("Unsupported ALU operation")

  def trace(self):
    """
    Handy function to print out the CPU state. You might want to call this
    from run() if you need help debugging.
    """
    print(f"TRACE: %02X | %02X %02X %02X |" % (
      self.pc,
      self.fl,
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

  def handle_jmp(self, reg_a):
    self.pc = self.reg[reg_a]

  def handle_cmp(self, reg_a, reg_b):
    self.alu('CMP', reg_a, reg_b)

  def handle_jeq(self, reg_a):
    if self.fl == 0b00000001:
      self.handle_jmp(reg_a)
  
  def handle_jne(self, reg_a):
    if self.fl != 0b00000001:
      self.handle_jmp(reg_a)

  def handle_and(self, reg_a, reg_b):
    self.alu('AND', reg_a, reg_b)

  def handle_or(self, reg_a, reg_b):
    self.alu('OR', reg_a, reg_b)

  def handle_xor(self, reg_a, reg_b):
    self.alu('XOR', reg_a, reg_b)

  def handle_not(self, reg_a):
    self.alu('NOT', reg_a)

  def handle_shl(self, reg_a, reg_b):
    self.alu('SHL', reg_a, reg_b)

  def handle_shr(self, reg_a, reg_b):
    self.alu('SHR', reg_a, reg_b)

  def handle_mod(self, reg_a, reg_b):
    self.alu('MOD', reg_a, reg_b)

  def handle_dec(self, reg_a):
    self.alu('DEC', reg_a)

  def handle_div(self, reg_a, reg_b):
    self.alu('DIV', reg_a, reg_b)

  def handle_inc(self, reg_a):
    self.alu('INC', reg_a)

  def handle_int(self, reg_a):
    if masked_interrupts == 0:
      self.reg[4] = 1 << self.reg[reg_a] - 1
      masked_interrupts = self.reg[4] & self.reg[5]
      if masked_interrupts > 0:
        vector = 0xf8 + math.log2(masked_interrupts)
        self.reg[5] = 0
        self.reg[7] -= 1
        self.ram_write(self.pc, self.reg[7])
        self.reg[7] -= 1
        self.ram_write(self.fl, self.reg[7])
        for i in range(7):
          self.handle_push(i)
        self.pc = self.ram_read(vector)

  def handle_iret(self):
    for i in range(6, -1, -1):
      self.pop(i)
    self.fl = self.ram_read(self.reg[7])
    self.reg[7] += 1
    self.pc = self.ram_read(self.reg[7])
    self.reg[7] += 1
    self.masked_interrupts = 0

  def handle_jge(self, reg_a):
    if self.fl != 0b00000100:
      self.handle_jmp(reg_a)

  def handle_jgt(self, reg_a):
    if self.fl == 0b00000010:
      self.handle_jgt(reg_a)

  def handle_jle(self, reg_a):
    if self.fl != 0b00000010:
      self.handle_jmp(reg_a)

  def handle_jlt(self, reg_a):
    if self.fl == 0b00000100:
      self.handle_jmp(reg_a)

  def handle_ld(self, reg_a, reg_b):
    self.reg[reg_a] = self.ram_read(self.reg[reg_b])

  def handle_nop(self):
    pass

  def handle_pra(self, reg_a):
    print(chr(self.reg[reg_a]))

  def handle_st(self, reg_a, reg_b):
    self.ram_write(self.reg[reg_b], self.reg[reg_a])
