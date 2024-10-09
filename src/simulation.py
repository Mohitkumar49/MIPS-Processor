from dis import Instruction
import utils



def read_Binary_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    data_memory = {}
    binary_instructions = []
    original_instructions = []  
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
        elif current_section == "code":
            if line:
                binary_instructions.append(line)
                original_instructions.append(line)  

    return binary_instructions, original_instructions, data_memory



class MIPS_Simulator:
    def __init__(self, binary_code,original_instructions, data_memory):
        self.registers = {f'$t{i}': 0 for i in range(8)}
        self.registers.update({f'$s{i}': 0 for i in range(8)})
        self.registers['$zero'] = 0
        self.registers['$1'] = 0  # Base address register
        self.registers['$ra'] = 0
        self.memory = data_memory
        self.binary_code = binary_code
        self.original_instructions = original_instructions 
        self.pc = 0
        self.result = 0

   
    def run(self):
        while self.pc < len(self.binary_code):
            instruction = self.fetch()
            self.decode(instruction)
            self.execute()
            self.write_back()
        
            original_instruction = self.original_instructions[self.pc]
            print(f"Instruction: {self.current_instruction}")
            print(f"Control Signals: {self.control_signals}")

            self.pc += 1

    def fetch(self):
        return self.binary_code[self.pc]

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
            
            parts = (op_code, rs, rt, rd, shamt, funct)
            self.current_instruction = ('R', parts)
            self.control_signals = self.generate_control_signals(op_code, 'R')

        elif op_code in utils.I_type_op_codes.values():
            rs = utils.binary_to_register[binary_instruction[6:11]]  
            rt = utils.binary_to_register[binary_instruction[11:16]]  
            immediate = binary_instruction[16:32]
            
            instruction_name = [key for key, value in utils.I_type_op_codes.items() if value == op_code]
            parts = (instruction_name[0], rs, rt, immediate)
            self.current_instruction = ('I', parts)
            self.control_signals = self.generate_control_signals(op_code, 'I')

        elif op_code in utils.J_type_op_codes.values():
            address = binary_instruction[6:32]
            
            instruction_name = [key for key, value in utils.J_type_op_codes.items() if value == op_code]
            parts = (instruction_name[0], address)
            self.current_instruction = ('J', parts)
            self.control_signals = self.generate_control_signals(op_code, 'J')
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
        rt_val = self.registers[rt]
        imm_val = int(immediate, 2) if immediate[0] == '0' else -((int(immediate[1:], 2) ^ 0xFFFF) + 1)

        if op_code == utils.I_type_op_codes['lw']:
            effective_address = rs_val + imm_val  # Calculate effective address
            self.result = self.memory.get(effective_address, 0)  # Load value from memory
        elif op_code == utils.I_type_op_codes['addi']:
            self.result = rs_val + imm_val
        elif op_code == utils.I_type_op_codes['beq']:
            if rs_val == rt_val:
                self.pc += imm_val - 1  # Adjust PC to branch to the target address
        elif op_code == utils.I_type_op_codes['bne']:
            if rs_val != rt_val:
                self.pc += imm_val - 1  # Adjust PC to branch to the target address


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
            
    
    def generate_control_signals(self, op_code, inst_type):
        control = {
            'RegWrite': 0,
            'MemRead': 0,
            'MemWrite': 0,
            'ALUOp': '00',
            'Jump': 0,
        }

        if inst_type == 'R':
            control['RegWrite'] = 1
            control['ALUOp'] = '10'  # Custom signal for R-type ALU operations

        elif inst_type == 'I':
            control['ALUOp'] = '00'  # ALU operation for I-type instructions
            if op_code in utils.I_type_op_codes.values():
                if op_code == utils.I_type_op_codes['lw']:
                    control['MemRead'] = 1
                    control['RegWrite'] = 1  # Write the loaded value into a register
                elif op_code == utils.I_type_op_codes['sw']:
                    control['MemWrite'] = 1
                elif op_code == utils.I_type_op_codes['addi']:
                    control['RegWrite'] = 1

        elif inst_type == 'J':
            control['Jump'] = 1

        return control


if __name__ == "__main__":
    binary_code, original_instructions, data_memory = read_Binary_file('outputs/binary_output_5.txt')
    
    simulator = MIPS_Simulator(binary_code,original_instructions, data_memory)
    print("\n")
    
    simulator.run()
        
    print("\n")
    print("Final register values:", ", ".join([f"{reg}: {value}" for reg, value in simulator.registers.items()]))
    
    

    
    

