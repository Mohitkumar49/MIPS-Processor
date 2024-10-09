from dis import Instruction
import utils

def read_Binary_file(file_path):
    # Reads the binary file and splits data memory and code sections.
    with open(file_path, 'r') as f:
        lines = f.readlines()

    data_memory = {}
    binary_instructions = []
    current_section = None

    for line in lines:
        line = line.strip()
        if line == "Data Memory:":
            current_section = "data"
        elif line == "Machine Code:":
            current_section = "code"
        elif current_section == "data" and ':' in line:
            var, addr = line.split(':')
            data_memory[var.strip()] = addr.strip()
        elif current_section == "code" and line:
            binary_instructions.append(line)

    return binary_instructions, data_memory

class MIPS_Simulator:
    def __init__(self, binary_code, data_memory):
        self.registers = {f'$t{i}': 0 for i in range(8)}
        self.registers.update({f'$s{i}': 0 for i in range(8)})
        self.registers['$zero'] = 0
        self.registers['$1'] = 0  # Base address register
        self.registers['$ra'] = 0
        self.memory = {var: int(addr, 2) for var, addr in data_memory.items()}
        self.binary_code = binary_code
        self.pc = 0
        self.result = 0

    def run(self):
        while self.pc < len(self.binary_code):
            instruction = self.fetch()
            self.decode(instruction)
            self.execute()
            self.write_back()
            self.pc += 1

    def fetch(self):
        return self.binary_code[self.pc]

    def decode(self, instruction):
        binary_instruction = instruction.replace(" ", "").strip()
        op_code = binary_instruction[:6]

        if op_code == '000000':  # R-type instructions
            rs = utils.get_register_name(binary_instruction[6:11])
            rt = utils.get_register_name(binary_instruction[11:16])
            rd = utils.get_register_name(binary_instruction[16:21])
            shamt = binary_instruction[21:26]
            funct = binary_instruction[26:32]
            
            # Find the instruction name using the funct code
            instruction_name = [key for key, value in utils.R_type_funct_codes.items() if value == funct]
            
            self.current_instruction = ('R', (instruction_name[0], rs, rt, rd, shamt))

        elif op_code in utils.I_type_op_codes.values():
            rs = utils.get_register_name(binary_instruction[6:11])
            rt = utils.get_register_name(binary_instruction[11:16])
            immediate = binary_instruction[16:32]
            
            # Find the instruction name using the opcode
            instruction_name = [key for key, value in utils.I_type_op_codes.items() if value == op_code]
            
            self.current_instruction = ('I', (instruction_name[0], rs, rt, immediate))

        elif op_code in utils.J_type_op_codes.values():
            address = binary_instruction[6:32]
            instruction_name = [key for key, value in utils.J_type_op_codes.items() if value == op_code]
            
            self.current_instruction = ('J', (instruction_name[0], address))

        else:
            raise Exception(f"Unknown instruction: {binary_instruction}")

    def get_register_name(binary_code):
        return [key for key, value in utils.Register_codes.items() if value == binary_code][0]
    
    def decode(self, instruction):
        binary_instruction = instruction.replace(" ", "").strip()
        op_code = binary_instruction[:6]

        if op_code == '000000':  # R-type instructions
            rs = utils.binary_to_register[binary_instruction[6:11]]  
            rt = utils.binary_to_register[binary_instruction[11:16]]  
            rd = utils.binary_to_register[binary_instruction[16:21]]  
            shamt = binary_instruction[21:26]
            funct = binary_instruction[26:32]

            self.current_instruction = ('R', (op_code, rs, rt, rd, shamt, funct))  # Include op_code

        elif op_code in utils.I_type_op_codes.values():
            rs = utils.binary_to_register[binary_instruction[6:11]]  
            rt = utils.binary_to_register[binary_instruction[11:16]]  
            immediate = binary_instruction[16:32]

            instruction_name = [key for key, value in utils.I_type_op_codes.items() if value == op_code]
            self.current_instruction = ('I', (instruction_name[0], rs, rt, immediate))

        elif op_code in utils.J_type_op_codes.values():
            address = binary_instruction[6:32]
            instruction_name = [key for key, value in utils.J_type_op_codes.items() if value == op_code]
            self.current_instruction = ('J', (instruction_name[0], address))
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

    def execute_R_type(self, parts):
        _, rs, rt, rd, shamt, funct = parts
        rs_val = self.registers[rs]
        rt_val = self.registers[rt]

        if funct == '100000':  # Add
            self.result = rs_val + rt_val
        elif funct == '100010':  # Sub
            self.result = rs_val - rt_val
        # Include other R-type instructions (AND, OR, SLT)...

    def execute_I_type(self, parts):
        op_code, rs, rt, immediate = parts
        rs_val = self.registers[rs]
        imm_val = int(immediate, 2) if immediate[0] == '0' else -((int(immediate[1:], 2) ^ 0xFFFF) + 1)

        if op_code == utils.I_type_op_codes['lw']:
            effective_address = rs_val + imm_val
            self.result = self.memory.get(effective_address, 0)
        elif op_code == utils.I_type_op_codes['addi']:
            self.result = rs_val + imm_val
        # Add handling for other I-type instructions like `beq`.

    def execute_J_type(self, parts):
        op_code, address = parts
        target_address = int(address, 2)

        if op_code == utils.J_type_op_codes['j']:
            self.pc = target_address - 1  # -1 to account for `self.pc += 1`
        elif op_code == utils.J_type_op_codes['jal']:
            self.registers['$ra'] = self.pc + 1
            self.pc = target_address - 1

    def write_back(self):
        inst_type, parts = self.current_instruction

        if inst_type == 'R':
            _, _, _, rd, _, _ = parts
            self.registers[rd] = self.result
        elif inst_type == 'I':
            _, _, rt, _ = parts
            self.registers[rt] = self.result

if __name__ == "__main__":
    binary_code, data_memory = read_Binary_file('outputs/binary_output_1.txt')
    
    simulator = MIPS_Simulator(binary_code, data_memory)
    
    simulator.run()
