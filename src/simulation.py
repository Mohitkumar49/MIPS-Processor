def read_simulation_file(file_path):
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
        elif current_section == "data":
            var, addr = line.split(':')
            data_memory[var.strip()] = addr.strip()
        elif current_section == "code":
            binary_instructions.append(line)

    return binary_instructions, data_memory

if __name__ == "__main__":
    binary_code, data_memory = read_simulation_file('outputs/simulation_output.txt')
    
    



