PRINT_TIM    =  0b00000001
HALT         =  0b10  # 2
PRINT_NUM    =  0b00000011  # opcode 3
SAVE         =  0b100
PRINT_REG    =  0b101    # opcode 5
ADD          =  0b110
PUSH         =  0b111
POP          =  0b1000   # opcode 8
CALL         =  0b1001
RET          =  0b1010

import sys

memory = [0] * 256 

def load_memory(file_name):
    try:
        address = 0
        with open(file_name) as file:
            for line in file:
                split_line = line.split('#')[0]
                command = split_line.strip()

                if command == '':
                    continue

                instruction = int(command, 2)
                memory[address] = instruction

                address += 1

    except FileNotFoundError:
        print(f'{sys.argv[0]}: {sys.argv[1]} file was not found')
        sys.exit()

if len(sys.argv) < 2:
    print("Please pass in a second filename: python3 in_and_out.py second_filename.py")
    sys.exit()

file_name = sys.argv[1]
load_memory(file_name)

# write a program to pull each command out of memory and execute
# We can loop over it!

# register aka memory
registers = [0] * 8

registers[7] = 0xA

# [0,0,99,0,0,0,0,0]
# R0-R7


pc = 0  # program counter
running = True
while running:
    command = memory[pc]

    if command == CALL:
        #get register number
        reg = memory[pc +1]
        
        #adress to jump to from the register
        address = registers[reg]

        #push command call onto the stack
        return_adress = pc+2

        #decrement stack pointer
        registers[7] -= 1
        sp = registers[7]
        #put return adress on the stack
        memory[sp] = return_adress

        #look at register jump to that adress
        pc = address-1 # so that it will not be incremented before executing

    if command == RET:
        #pop return adress of stack
        sp = registers[7]
        return_adress = memory[sp]
        registers[7] += 1

        pc = return_adress-1 # so that it will not be incremented before executing

    if command == PRINT_TIM:
        print("Tim!")

    if command == HALT:
        running = False

    if command == PRINT_NUM:
        num_to_print = memory[pc + 1]
        print(num_to_print)
        pc += 1

    if command == SAVE:
        reg = memory[pc + 1]
        num_to_save = memory[pc + 2]
        registers[reg] = num_to_save

        pc += 2

    if command == PRINT_REG:
        reg_index = memory[pc + 1]
        print(registers[reg_index])
        pc += 1

    if command == ADD:
        first_reg = memory[pc + 1]
        sec_reg = memory[pc + 2]
        registers[first_reg] = registers[first_reg] + registers[sec_reg]
        pc += 2

    if command == PUSH:
        # decrement the stack pointer
        registers[7] -= 1

        # get the register number
        reg = memory[pc + 1]
        # get a value from the given register
        value = registers[reg]

        # put the value at the stack pointer address
        sp = registers[7]
        memory[sp] = value

        pc += 1

        
    if command == POP:
       # get the stack pointer (where do we look?)
       sp = registers[7]

       # get register number to put value in
       reg = memory[pc + 1]

       # use stack pointer to get the value
       value = memory[sp]
       # put the value into the given register
       registers[reg] = value
        # increment our stack pointer
       registers[7] += 1

        # increment our program counter
       pc += 1
        
    pc += 1