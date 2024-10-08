from dis import Instruction
import utils

def read_Binary_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    data_memory = {}
    binary_instructions = []
    
    current_section = None

    for line in lines:
        line = line.strip()  # Remove any leading/trailing whitespace
        if line == "Data Memory:":
            current_section = "data"
        elif line == "Machine Code:":
            current_section = "code"
        elif current_section == "data":
            if ':' in line:  # Check if the line contains a colon
                var, addr = line.split(':')
                data_memory[var.strip()] = addr.strip()  # Store variable names and addresses
        elif current_section == "code":
            if line:  # Ensure the line is not empty
                binary_instructions.append(line)  # Append binary instruction

    return binary_instructions, data_memory

    
        
        
class MIPS_Simulator:
    def __init__(self, binary_code, data_memory):
        # Initialize registers (32 registers)
        self.registers = {f'$t{i}': 0 for i in range(8)}  
        self.registers.update({f'$s{i}': 0 for i in range(8)})  
        self.registers['$zero'] = 0  
        self.registers['$1'] = 0  # Assume $1 is used for base address
        self.registers['$ra'] = 0  
 
        self.memory = {}
        for var, addr in data_memory.items():
            self.memory[var] = int(addr, 2)  # Convert binary address to integer value

        self.binary_code = binary_code
        self.pc = 0
        self.result = 0  # Store the result of the current instruction

    def run(self):
        while self.pc < len(self.binary_code):
            instruction = self.fetch() 
            self.decode(instruction)    
            self.execute()              
            self.write_back()           
            self.pc += 1                # Move to the next instruction

    def fetch(self):
        return self.binary_code[self.pc]
    
            
            
    def decode(self, instruction):
        binary_instruction = instruction.replace(" ", "").strip()
        op_code = binary_instruction[:6] 

        if op_code == '000000':  # R-type instructions have opcode '000000'
            rs = binary_instruction[6:11]
            rt = binary_instruction[11:16]
            rd = binary_instruction[16:21]
            shamt = binary_instruction[21:26]
            funct = binary_instruction[26:32]
            self.current_instruction = ('R', (op_code, rs, rt, rd, shamt, funct))

        elif op_code in utils.I_type_op_codes:
            rs = binary_instruction[6:11]
            rt = binary_instruction[11:16]
            immediate = binary_instruction[16:32]
            self.current_instruction = ('I', (op_code, rs, rt, immediate))

        elif op_code in utils.J_type_op_codes:
            address = binary_instruction[6:32]
            self.current_instruction = ('J', (op_code, address))

        else:
            raise Exception(f"Unknown instruction: {binary_instruction}")

            
        
    def execute(self):
        inst_type, parts = self.current_instruction

        if inst_type == 'R':
            self.execute_R_type(parts)
        elif inst_type == 'I':
            self.execute_I_type(parts)
        elif inst_type == 'J':
            self.execute_J_type(parts)

    def write_back(self):
        inst_type, parts = self.current_instruction

        if inst_type == 'R':
            rd = parts[3]  # Destination register (rd)
            self.registers[rd] = self.result

        elif inst_type == 'I':
            rt = parts[2]  # Target register (rt)
            self.registers[rt] = self.result

    def execute_R_type(self, parts):
        funct = parts[5]
        rd = parts[3]
        rs = parts[1]
        rt = parts[2]

        if funct == 'add':
            self.result = self.registers[rs] + self.registers[rt]
        elif funct == 'sub':
            self.result = self.registers[rs] - self.registers[rt]
        # Add other R-type functions as needed

    def execute_I_type(self, parts):
        op_code = parts[0]
        rs = parts[1]
        rt = parts[2]
        
        immediate = int(parts[3], 2)
        

        if op_code == 'lw':
            base_register_value = self.registers[rs]
            effective_address = base_register_value + immediate

        elif op_code == 'addi':
            rs = parts[1]
            immediate = int(parts[3])
            self.result = self.registers[rs] + immediate
        

    def execute_J_type(self, parts):
        op_code = parts[0]
        address = int(parts[1], 2)  

        if op_code == 'j':
            self.pc = address  # Jump to the specified address
        elif op_code == 'jal':
            self.registers['$ra'] = self.pc + 1  # Save return address in $ra
            self.pc = address  # Jump to the specified address
        elif op_code == 'jr':
            rs = parts[1]
            self.pc = self.registers[rs]  # Set the program counter to the address in the register




if __name__ == "__main__":
    binary_code, data_memory = read_Binary_file('outputs/binary_output.txt')
    
    simulator = MIPS_Simulator(binary_code, data_memory)
    simulator.run()
