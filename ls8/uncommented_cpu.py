"""CPU functionality."""

import sys

HLT = 1
LDI = 10000010 
PRN = 1000111
PUSH = 1000101 
POP = 1000110 
MUL = 10100010
ADD = 10100000
CALL = 1010000
RET = 10001 

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 0xFF
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0
        self.fl = [0] * 8
        self.dispach_table = {
            LDI: self.ldi,
            PRN: self.prn,
            PUSH: self.push,
            POP: self.pop,
            MUL: self.alu,
            ADD: self.alu,
            CALL: self.call,
            RET: self.return_from_call
        }

    def ram_read(self, MAR): 
        if MAR < len(self.ram):
            return self.ram[MAR]
        else:
            return None

    def ram_write(self, MAR, MDR): 
        self.ram[MAR] = MDR


    def load(self, program = None):
        """Load a program into memory."""

        if len(sys.argv) < 2:
            print("Please pass in a second filename: python3 in_and_out.py second_filename.py")
            sys.exit()

        try:
            address = 0
            with open(program) as file:
                for line in file:
                    split_line = line.split('#')[0]
                    command = split_line.strip()

                    if command == '':
                        continue

                    instruction = int(command)
                    self.ram[address] = instruction

                    address += 1

        except FileNotFoundError:
            print(f'{sys.argv[0]}: {sys.argv[1]} file was not found')
            sys.exit()

    def alu(self, reg_a, reg_b):
        """ALU operations."""
        ir = self.ram_read(self.pc)
        if ir == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif ir == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")
        self.pc += 3

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
    
    def convert(self, binary):
        binary_str = str(binary)
        binary_str.replace("0b", '')
        return int(binary_str, 2) 

    def ldi(self, reg_num, value):
        self.reg[reg_num] = value
        self.pc += 3

    def prn(self, reg_num, unused_operand):
        print(self.reg[reg_num])
        self.pc += 2

    def push(self, reg_num, unused_operand):
        self.reg[7] -= 1
        value = self.reg[reg_num]
        sp = self.reg[7]
        self.ram[sp] = value
        self.pc += 2

    def pop(self, reg_num, unused_operand):
        sp = self.reg[7]
        value = self.ram[sp]
        self.reg[reg_num] = value
        self.reg[7] += 1
        self.pc += 2

    def call(self, reg_num, unused_operand):
        address = self.reg[reg_num]
        return_address = self.pc+2
        self.reg[7] -= 1
        sp = self.reg[7]
        self.ram[sp] = return_address
        self.pc = address

    def return_from_call(self, unused_operand_1, unused_operand_2):
        sp = self.reg[7]
        return_address = self.ram[sp]
        self.reg[7] += 1
        self.pc = return_address

    def run(self):
        """Run the CPU."""
        ir = self.ram_read(self.pc)
        while ir != HLT:
            operand_a = self.convert(self.ram_read(self.pc+1))
            operand_b = self.convert(self.ram_read(self.pc+2))

            self.dispach_table[ir](operand_a, operand_b)
            ir = self.ram_read(self.pc)