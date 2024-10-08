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
        self.registers = {f'$t{i}': 0 for i in range(8)}  # Temporary registers
        self.registers.update({f'$s{i}': 0 for i in range(8)})  # Saved registers
        self.registers['$zero'] = 0  # $zero register
        self.registers['$1'] = 0  # Assume $1 is used for base address

        # Initialize memory
        self.memory = {}
        for var, addr in data_memory.items():
            self.memory[var] = int(addr, 2)  # Convert binary address to integer value

        # Load the binary instructions
        self.binary_code = binary_code
        # Initialize the program counter
        self.pc = 0

    def run(self):
        while self.pc < len(self.binary_code):
            instruction = self.fetch()  # Fetch instruction
            self.decode(instruction)     # Decode the instruction
            self.execute()               # Execute the instruction
            self.write_back()            # Write back the results
            self.pc += 1                 # Move to the next instruction

    def fetch(self):
        """
        Fetches the instruction at the current program counter (PC).

        Returns:
        - str: The fetched instruction.
        """
        return self.binary_code[self.pc]

    def decode(self, instruction):
        """
        Decodes the fetched instruction.

        Parameters:
        - instruction (str): The fetched instruction.
        """
        parts = instruction.split()
        op_code = parts[0]

        if op_code in utils.R_type_funct_codes:
            self.current_instruction = ('R', parts)
        elif op_code in utils.I_type_op_codes:
            self.current_instruction = ('I', parts)
        elif op_code in utils.J_type_op_codes:
            self.current_instruction = ('J', parts)
        else:
            raise Exception(f"Unknown instruction: {instruction}")

    def execute(self):
        """
        Executes the current instruction based on its type.
        """
        inst_type, parts = self.current_instruction

        if inst_type == 'R':
            self.execute_R_type(parts)
        elif inst_type == 'I':
            self.execute_I_type(parts)
        elif inst_type == 'J':
            self.execute_J_type(parts)

    def write_back(self):
        """
        Writes results back to registers or memory if necessary.
        This can be extended to include actual writing to registers.
        """
        pass  # Implement this method based on specific needs

    def execute_R_type(self, parts):
        """
        Executes R-type instructions.

        Parameters:
        - parts (list): List containing the parts of the instruction.
        """
        funct = parts[0]
        rd = parts[1]
        rs = parts[2]
        rt = parts[3]

        if funct == 'add':
            self.registers[rd] = self.registers[rs] + self.registers[rt]
        elif funct == 'sub':
            self.registers[rd] = self.registers[rs] - self.registers[rt]
        # Add other R-type functions as needed

    def execute_I_type(self, parts):
        """
        Executes I-type instructions.

        Parameters:
        - parts (list): List containing the parts of the instruction.
        """
        op_code = parts[0]
        rt = parts[1]

        if op_code == 'lw':
            # Load word from memory into register
            offset, base = parts[2].split('(')  # e.g., 0($1)
            base = base.strip(')')  # Get register name
            offset = int(offset)  # Convert offset to integer

            # Calculate the effective address and load value into the register
            effective_address = self.registers[base] + offset
            self.registers[rt] = self.memory.get(format(effective_address, '032b'), 0)
        elif op_code == 'addi':
            rs = parts[2]
            immediate = int(parts[3])
            self.registers[rt] = self.registers[rs] + immediate
        # Handle other I-type instructions as needed

    def execute_J_type(self, parts):
        """
        Executes J-type instructions.

        Parameters:
        - parts (list): List containing the parts of the instruction.
        """
        # Handle jump instructions
        pass  # Implement based on J-type instructions

if __name__ == "__main__":
    # Read binary code and data memory from the simulation output file
    binary_code, data_memory = read_Binary_file('outputs/simulation_output.txt')
    
    # Create an instance of the MIPS simulator
    simulator = MIPS_Simulator(binary_code, data_memory)
    simulator.run()
