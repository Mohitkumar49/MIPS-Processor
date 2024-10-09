import os
import utils
from read import read_asm_file

def compile(assembly):
    binary_code = []
    data_section = False
    text_section = False
    data_memory = {}
    label_addresses = {}
    instructions = []
    
    # Initialize register $1 with the base address for the first variable
    
    register_base_address = '00000000000000000000000000000001'  
    

    line_count = 0
    for line in assembly:
        line = line.strip()

        if line == '.data':
            data_section = True
            text_section = False
        elif line == '.text':
            data_section = False
            text_section = True
        elif data_section:
            handle_data_section(line, data_memory)
        elif text_section:
            if line.endswith(':'):
                # Store label with its address
                label_name = line.replace(':', '')
                label_addresses[label_name] = line_count
            else:
                instructions.append(line)
                line_count += 1

    # generate binary code for instructions
    for line in instructions:
        instruction = convert(line, data_memory, label_addresses, instructions.index(line))  
        if instruction:
            binary_code.append(instruction)

    return binary_code, data_memory

def handle_data_section(line, data_memory):
    parts = line.split(':')
    if len(parts) == 2 and '.word' in parts[1]:
        var_name = parts[0].strip()
        value = parts[1].split()[1]  # Get the number after .word
        
        # Assume the address for variables starts from a fixed base
        address = len(data_memory) * 4  
        data_memory[var_name] = (format(address, '032b'), value)

def convert(line, data_memory, label_addresses, current_line_index):
    parts = [part.strip(',') for part in line.split()]

    if parts[0] in utils.R_type_funct_codes:
        instruction = parse_R_type(parts)
    elif parts[0] in utils.I_type_op_codes:
        instruction = parse_I_type(parts, data_memory, label_addresses, current_line_index)  
    elif parts[0] in utils.J_type_op_codes:
        instruction = parse_J_type(parts, label_addresses)
    else:
        return None  

    return instruction

def parse_R_type(parts):
    op_code = '000000'
    shamt = '00000'
    funct = utils.R_type_funct_codes[parts[0]]

    rd = utils.Register_codes[parts[1]]
    rs = utils.Register_codes[parts[2]]
    rt = utils.Register_codes[parts[3]]

    return op_code + " " + rs + " " + rt + " " + rd + " " + shamt + " " + funct

def parse_I_type(parts, data_memory, label_addresses, current_line_index):
    instruction = parts[0]
    op_code = utils.I_type_op_codes[instruction]

    if instruction == 'lw':
        rt = utils.Register_codes[parts[1]]
        variable_name = parts[2]
        
        # Get the address and calculate the offset
        variable_address, _ = data_memory[variable_name]
        base = '$1'
        rs = utils.Register_codes[base]
        offset = format(int(variable_address, 2), '016b')  # Convert the address to a 16-bit offset

        return op_code + " " + rs + " " + rt + " " + offset
    elif instruction == 'beq':
        rs = utils.Register_codes[parts[1]]
        rt = utils.Register_codes[parts[2]]
        
        # Calculate offset for the branch target
        target_label = parts[3]
        if target_label in label_addresses:
            target_line_index = label_addresses[target_label]
            offset = target_line_index - (current_line_index + 1)  # Offset relative to the next instruction
            offset = format(offset & 0xFFFF, '016b')  # Convert to 16-bit signed binary
        else:
            raise ValueError(f"Label '{target_label}' not found for 'beq' instruction.")

        return op_code + " " + rs + " " + rt + " " + offset
    elif instruction == 'addi':
        rs = utils.Register_codes[parts[2]]
        rt = utils.Register_codes[parts[1]]
        
        immediate = format(int(parts[3]), '016b')

        return op_code + " " + rs + " " + rt + " " + immediate
    else:
        return None 

def parse_J_type(parts, label_addresses):
    instruction = parts[0]
    op_code = utils.J_type_op_codes[instruction]

    # Get the target label and convert its address
    target_label = parts[1]
    if target_label in label_addresses:
        target_address = label_addresses[target_label] * 4  # Each instruction is 4 bytes apart
        address = format(target_address >> 2, '026b')  # Shift right by 2 for MIPS J format
    else:
        raise ValueError(f"Label '{target_label}' not found for 'j' instruction.")

    return op_code + " " + address

def print_output(binary_code, data_memory):
    os.makedirs('outputs', exist_ok=True) 
    with open('outputs/binary_output_5.txt', 'w') as f:
        f.write("Data Memory:\n")
        for var, (addr, value) in data_memory.items():
            f.write(f"{var}: {addr}\n")  # Use the binary address
        f.write("\nMachine Code:\n")
        for code in binary_code:
            f.write(f"{code}\n")

if __name__ == "__main__":
    assembly_code = read_asm_file('inputs/test_code_5.asm')  
    binary_code, data_memory = compile(assembly_code)
    print_output(binary_code, data_memory)
