import os
# from Output_Code_1.data_memory_1 import data_memory
# from Output_Code_2.data_memory_2 import data_memory

# Simulating 32 Registers (General Purpose Registers for MIPS)
class Registers:
    def _init_(self):
        self.registers = {
        0:  "00000",  # $zero
        1:  "00001",  # $at (Assembler temporary)
        2:  "00010",  # $v0 (Return value)
        3:  "00011",  # $v1 (Return value)
        4:  "00100",  # $a0 (Argument)
        5:  "00101",  # $a1 (Argument)
        6:  "00110",  # $a2 (Argument)
        7:  "00111",  # $a3 (Argument)
        8:  "01000",  # $t0 (Temporary)
        9:  "01001",  # $t1 (Temporary)
        10: "01010",  # $t2 (Temporary)
        11: "01011",  # $t3 (Temporary)
        12: "01100",  # $t4 (Temporary)
        13: "01101",  # $t5 (Temporary)
        14: "01110",  # $t6 (Temporary)
        15: "01111",  # $t7 (Temporary)
        16: "10000",  # $s0 (Saved)
        17: "10001",  # $s1 (Saved)
        18: "10010",  # $s2 (Saved)
        19: "10011",  # $s3 (Saved)
        20: "10100",  # $s4 (Saved)
        21: "10101",  # $s5 (Saved)
        22: "10110",  # $s6 (Saved)
        23: "10111",  # $s7 (Saved)
        24: "11000",  # $t8 (Temporary)
        25: "11001",  # $t9 (Temporary)
        26: "11010",  # $k0 (Reserved for OS kernel)
        27: "11011",  # $k1 (Reserved for OS kernel)
        28: "11100",  # $gp (Global pointer)
        29: "11101",  # $sp (Stack pointer)
        30: "11110",  # $fp (Frame pointer)
        31: "11111",  # $ra (Return address)
    }

    def read(self, reg_num):
        # print("reg_num", reg_num )
        return self.registers[reg_num]

    def write(self, reg_num, value):
        if reg_num != 0:  # Register $zero is always 0
            self.registers[reg_num] = value

# ALU Simulation
class ALU:
    def execute(self, control, input1, input2):
        # Map the binary function codes to ALU operations
        if control == '100000':  # add
            # print("add")
            return input1 + input2
        elif control == '100010':  # sub
            # print("sub")
            return input1 - input2
        elif control == '100100':  # and
            # print("and")
            return input1 & input2
        elif control == '100101':  # or
            # print("or")
            return input1 | input2
        elif control == '101010':  # slt
            # print("slt")
            return 1 if input1 < input2 else 0
        else:
            raise ValueError(f"Unknown ALU operation: {control}")

# Main Memory Simulation
class Memory:
    def _init_(self):
        self.memory = {} 

    def load(self, address):
        return self.memory.get(address, 0) 

    def store(self, address, value):
        self.memory[address] = value

class ControlUnit:
    def _init_(self):
        self.signals = {}

    def generate_control_signals(self, instruction_type):
        if instruction_type == 'R':
            self.signals = {
                'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1, 
                'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'ALUOp': 'R-type'
            }
        elif instruction_type == 'lw':
            self.signals = {
                'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 1, 'RegWrite': 1,
                'MemRead': 1, 'MemWrite': 0, 'Branch': 0, 'ALUOp': 'add'
            }
        elif instruction_type == 'sw':
            self.signals = {
                'RegDst': 'X', 'ALUSrc': 1, 'MemToReg': 'X', 'RegWrite': 0,
                'MemRead': 0, 'MemWrite': 1, 'Branch': 0, 'ALUOp': 'add'
            }
        elif instruction_type == 'beq':
            self.signals = {
                'RegDst': 'X', 'ALUSrc': 0, 'MemToReg': 'X', 'RegWrite': 0,
                'MemRead': 0, 'MemWrite': 0, 'Branch': 1, 'ALUOp': 'sub'
            }
        elif instruction_type == 'j':
            self.signals = {
                'RegDst': 'X', 'ALUSrc': 'X', 'MemToReg': 'X', 'RegWrite': 0,
                'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 1
            }
        elif instruction_type == 'addi':
            self.signals = {
                'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 0, 'RegWrite': 1,
                'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'ALUOp': 'add'
            }
        else:
            raise ValueError(f"Unknown instruction type: {instruction_type}")

class MIPS_Simulator:
    def _init_(self, binary_code, data_memory):
        self.registers = Registers()
        self.alu = ALU()
        self.memory = Memory()
        self.control_unit = ControlUnit()
        self.binary_code = binary_code
        self.data_memory = data_memory
        # self.binary_code = self.load_machine_code(filepath + "machine_code.txt")
        # self.data_memory =  data_memory #self.load_machine_code(filepath + "data_memory.py")
        self.pc = 0

    def load_machine_code(self, filepath):
        """Load machine code from a file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"The file {filepath} does not exist.")
        
        with open(filepath, 'r') as file:
            machine_code = file.readlines()
        
        # Remove any extra whitespace and newlines
        machine_code = [line.strip() for line in machine_code if line.strip()]
        return machine_code

    def fetch(self):
        """Fetch the instruction at the current PC."""
        if self.pc < len(self.binary_code):
            instruction = self.binary_code[self.pc]
            self.pc += 1
            return instruction
        else:
            return None

    def decode(self, instruction):
        """Decode the instruction and generate control signals."""
        opcode = instruction[:6]
        if opcode == '000000':  # R-type instruction
            funct = instruction[26:] 
            return 'R', funct
        elif opcode == '100011':  # lw
            return 'lw', None
        elif opcode == '101011':  # sw
            return 'sw', None
        elif opcode == '000100':  # beq
            return 'beq', None
        elif opcode == '000010':  # j
            return 'j', None
        elif opcode == '001000':  # addi
            return 'addi', None
        else:
            raise ValueError(f"Unknown opcode: {opcode}")


    def execute(self):
        """Simulate the entire MIPS pipeline."""
        while self.pc < len(self.binary_code):
            instruction = self.fetch()
            if not instruction:
                break

            instruction_type, operation = self.decode(instruction)
            self.control_unit.generate_control_signals(instruction_type)
            
            if instruction_type == 'R':
                rs = self.registers.read(int(instruction[6:11], 2))
                # print("rs ", rs)
                rt = self.registers.read(int(instruction[11:16], 2))
                # print("rt ", rt)
                rd = int(instruction[16:21], 2)
                # print("rd ", rd)
                result = self.alu.execute(operation, rs, rt)
                if self.control_unit.signals['RegWrite']:
                    self.registers.write(rd, result)
                    # print("rd ", rd, "value = ", result)
            elif instruction_type == 'lw':
                base = self.registers.read(int(instruction[6:11], 2))
                # print("base = ", base)
                offset = int(instruction[16:], 2)
                # print("offset = ", offset)
                address = int(base) + offset
                # print("address = ", address)
                # data = self.memory.load(address)
                data = self.data_memory[address]
                # print("data = ", data)
                rt = int(instruction[11:16], 2)
                # print("rt ", rt)
                if self.control_unit.signals['RegWrite']:
                    self.registers.write(rt, data)
                    # print("rt ", rt, "value = ", data)
            elif instruction_type == 'beq':
                # print("Branch")
                rs = self.registers.read(int(instruction[6:11], 2))
                # print("rs ", rs)
                rt = self.registers.read(int(instruction[11:16], 2))
                # print("rt ", rt)
                if rs == rt and self.control_unit.signals['Branch']:
                    offset = int(instruction[16:], 2) - 2
                    # print("offset = ", offset)
                    self.pc += offset
            elif instruction_type == 'addi':
                rs = self.registers.read(int(instruction[6:11], 2))
                # print("rs ", rs)
                immediate = int(instruction[16:], 2) 
                rt = int(instruction[11:16], 2)
                # print("rt ", rt)
                result = rs + immediate 
                if self.control_unit.signals['RegWrite']:
                    self.registers.write(rt, result)
                    # print("rt ", rt, "value = ", result)
            elif instruction_type == 'j':
                address = int(instruction[6:], 2)
                self.pc = address

        
            print(self.control_unit.signals)

    def run(self):
        """Run the MIPS program until all instructions are executed."""
        self.execute()


# # Example usage:
binary_code_1 = [
    '10001100000010000000000000000000',  # lw $t0, num1
    '10001100000010010000000000000100',  # lw $t1, num2
    '00000001000010010101000000100000',  # add $t2, $t0, $t1
    '00000001001010000101100000100010',  # sub $t3, $t1, $t0
    '00000001000010010110000000100100',  # and $t4, $t0, $t1
    '00000001000010010110100000100101',  # or  $t5, $t0, $t1
    '00000001000010010111000000101010',  # slt $t6, $t0, $t1
]

data_memory_1 = {
    0: 10,  # num1
    4: 20   # num2
}

# Test Code 2 Binary Instructions
binary_code_2 = [
    '10001100000010000000000000000000',  # lw $t0, val1
    '10001100000010010000000000000100',  # lw $t1, val2
    '00100001000010100000000000001010',  # addi $t2, $t0, 10
    '00010001000010010000000000000100',  # beq $t0, $t1, equal_case
    '00000001000010010101100000100010',  # sub $t3, $t0, $t1
    '00001000000000000000000000000111',  # j end
    '00000001000010010101100000100000',  # equal_case: add $t3, $t0, $t1
]

data_memory_2 = {
    0: 5,  # val1
    4: 5   # val2
}


# Running Test Code 1
simulator_1 = MIPS_Simulator(binary_code_1, data_memory_1)
simulator_1.run()
print("Test Code 1 - Signal Values:")
print(simulator_1.control_unit.signals)

print("Test Code 1 - Register Values after execution:")

# Correctly iterating over register numbers and printing their values
for i in range(32):  # Since there are 32 registers
    print(f"Register {i}  {simulator_1.registers.read(i)}")

# Running Test Code 2
simulator_2 = MIPS_Simulator(binary_code_2, data_memory_2)
simulator_2.run()
print("Test Code 2 - Signal Values:")
print(simulator_2.control_unit.signals)

print("Test Code 2 - Register Values after execution:")

# Correctly iterating over register numbers and printing their values
for i in range(32):  # Since there are 32 registers
    print(f"Register {i}  {simulator_2.registers.read(i)}")