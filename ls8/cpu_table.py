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
        # +-----------------------+
        # | FF  I7 vector         |    Interrupt vector table
        # | FE  I6 vector         |
        # | FD  I5 vector         |
        # | FC  I4 vector         |
        # | FB  I3 vector         |
        # | FA  I2 vector         |
        # | F9  I1 vector         |
        # | F8  I0 vector         |
        # | F7  Reserved          |
        # | F6  Reserved          |
        # | F5  Reserved          |
        # | F4  Key pressed       |    Holds the most recent key pressed on the keyboard
        # | F3  Start of Stack    |
        # | F2  [more stack]      |    Stack grows down
        # | ...                   |
        # | 01  [more program]    |
        # | 00  Program entry     |    Program loaded upward in memory starting at 0
        # +-----------------------+
        # * RAM is cleared to `0`.
        self.ram = [0] * 0xFF
        # * `R0`-`R6` are cleared to `0`.
        #R5 is reserved as the interrupt mask (IM)
        #R6 is reserved as the interrupt status (IS)
        #R7 is reserved as the stack pointer (SP)
        self.reg = [0] * 8
        # * `R7` is set to `0xF4`.
        self.reg[7] = 0xF4
        # `PC`: Program Counter, address of the currently executing instruction
        # * `PC` and `FL` registers are cleared to `0`.
        self.pc = 0
        # * `FL`: Flags, see below  
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
        
    # Inside the CPU, there are two internal registers used for memory operations: the Memory Address Register (MAR) and the Memory Data Register (MDR). The MAR contains the address that is being read or written to. The MDR contains the data that was read or the data to write. You don't need to add the MAR or MDR to your CPU class, but they would make handy parameter names for ram_read() and ram_write(), if you wanted.   
    # * `MAR`: Memory Address Register, holds the memory address we're reading or writing
    # * `MDR`: Memory Data Register, holds the value to write or the value just read

    def ram_read(self, MAR): 
    # should accept the address to read and return the value stored there.
        if MAR < len(self.ram):
            return self.ram[MAR]
        else:
            return None

    def ram_write(self, MAR, MDR): 
    # should accept a value to write, and the address to write it to. 
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
                    self.ram_write(address, instruction)

                    address += 1

        except FileNotFoundError:
            print(f'{sys.argv[0]}: {sys.argv[1]} file was not found')
            sys.exit()

    def alu(self, reg_a, reg_b):
        """ALU operations."""
        ir = self.ram_read(self.pc)
        if ir == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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
        # decrement the stack pointer
        self.reg[7] -= 1
        # get a value from the given register
        value = self.reg[reg_num]
        # put the value at the stack pointer address
        sp = self.reg[7]
        self.ram_write(sp, value)
        self.pc += 2

    def pop(self, reg_num, unused_operand):
        # get the stack pointer (where do we look?)
        sp = self.reg[7]
        # use stack pointer to get the value
        value = self.ram_read(sp)
        # put the value into the given register
        self.reg[reg_num] = value
        # increment our stack pointer
        self.reg[7] += 1
        self.pc += 2

    def call(self, reg_num, unused_operand):
        ### get the address to jump to, from the register
        address = self.reg[reg_num]
        ### push command after CALL onto the stack
        return_address = self.pc+2
        ### decrement stack pointer
        self.reg[7] -= 1
        sp = self.reg[7]
        ### put return address on the stack
        self.ram_write(sp, return_address)
        ### then look at register, jump to that address
        self.pc = address

    def return_from_call(self, unused_operand_1, unused_operand_2):
        # pop the return address off the stack
        sp = self.reg[7]
        return_address = self.ram_read(sp)
        self.ram_write(sp, return_address)
        self.reg[7] += 1
        # go to return address: set the pc to return address
        self.pc = return_address

    def run(self):
        """Run the CPU."""
        # * `IR`: Instruction Register, contains a copy of the currently executing instruction
        ir = self.ram_read(self.pc)
        while ir != HLT:
            # Using ram_read(), read the bytes at PC+1 and PC+2 from RAM into variables operand_a and operand_b in case the instruction needs them.
            operand_a = self.convert(self.ram_read(self.pc+1))
            operand_b = self.convert(self.ram_read(self.pc+2))

            self.dispach_table[ir](operand_a, operand_b)
            ir = self.ram_read(self.pc)