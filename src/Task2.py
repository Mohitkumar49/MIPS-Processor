# MIPS Simulator in Python

# Initialize Memory and Registers
memory = {}
registers = {
    "$zero": 0, "$1": 0,  # Assuming $1 will hold the base address
    "$t0": 0, "$t1": 0, "$t2": 0,
    "$t3": 0, "$t4": 0, "$t5": 0, "$t6": 0,
    "$t7": 0, "$s0": 0, "$s1": 0, "$s2": 0,
    "$s3": 0, "$s4": 0, "$s5": 0, "$s6": 0,
    "$s7": 0, "$t8": 0, "$t9": 0, "$k0": 0,
    "$k1": 0, "$gp": 0, "$sp": 0, "$fp": 0,
    "$ra": 0
}
pc = 0x00400000  # Program Counter (assumed starting address)

# Load Memory and Initialize Registers
data_segment_address = 0x10000000  # Starting address for data segment

# Opcode and Function Code Mappings
opcode_map = {
    "lw": "100011",
    "add": "000000",
    "and": "000000",
    "or": "000000",
    "slt": "000000",
}

funct_map = {
    "add": "100000",
    "sub": "100010",
    "and": "100100",
    "or": "100101",
    "slt": "101010",
}

register_map = {
    "$zero": "00000", "$1": "00001", "$t0": "01000", "$t1": "01001",
    "$t2": "01010", "$t3": "01011", "$t4": "01100", "$t5": "01101",
    "$t6": "01110", "$t7": "01111", "$s0": "10000", "$s1": "10001",
    "$s2": "10010", "$s3": "10011", "$s4": "10100", "$s5": "10101",
    "$s6": "10110", "$s7": "10111", "$t8": "11000", "$t9": "11001",
    "$k0": "11010", "$k1": "11011", "$gp": "11100", "$sp": "11101",
    "$fp": "11110", "$ra": "11111"
}

# Function to Load and Parse Assembly File
def load_asm_file(filename):
    data_segment = {}
    instruction_memory = []
    current_section = None

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith(".data"):
                current_section = "data"
                continue
            elif line.startswith(".text"):
                current_section = "text"
                continue

            if current_section == "data":
                if ':' in line:  # Handle data definitions
                    label, value = line.split(':')
                    label = label.strip()
                    value = value.split()[1]  # Get the value after .word
                    data_segment[label] = int(value)
            elif current_section == "text":
                if line:  # Ignore empty lines
                    instruction_memory.append(line)

    return data_segment, instruction_memory

# Function to Translate Assembly to Binary
def translate_assembly_to_binary(instruction):
    parts = instruction.split()
    op = parts[0]

    if op in ["add", "sub", "and", "or", "slt"]:
        # R-type: add $t2, $t0, $t1
        rd = register_map[parts[1].strip(",")]
        rs = register_map[parts[2].strip(",")]
        rt = register_map[parts[3]]
        opcode = opcode_map[op]
        funct = funct_map[op]
        binary_instruction = f"{opcode}{rs}{rt}{rd}00000{funct}"
    
    elif op == "lw":
        rt = register_map[parts[1].strip(",")]
        # Convert the instruction to the format lw rt, 0($1)
        base = register_map["$1"]  # Assuming the address is in $1
        binary_instruction = f"{opcode_map[op]}{base}{rt}0000000000000000"  # Assuming offset is 0

    return binary_instruction

# Function to Fetch Instruction
def instruction_fetch(pc, instruction_memory):
    index = (pc - 0x00400000) // 4  # Adjusting PC for the instruction memory
    if 0 <= index < len(instruction_memory):
        return instruction_memory[index]
    else:
        raise ValueError("Program counter out of bounds.")

# Function to Decode Instruction
def instruction_decode(instruction):
    # Split the instruction into parts for decoding
    parts = instruction.split()
    op = parts[0]
    return {
        'op': op,
        'rd': parts[1].strip(",") if op != 'lw' else parts[1].strip(","),
        'rs': parts[2].strip(",") if op in ["add", "sub", "and", "or", "slt"] else None,
        'rt': parts[3] if op in ["add", "sub", "and", "or", "slt"] else None,
    }

# Function to Execute Instruction
def execute(decoded_fields, registers):
    op = decoded_fields['op']
    if op in ["add", "sub", "and", "or", "slt"]:
        rs = registers[decoded_fields['rs']]
        rt = registers[decoded_fields['rt']]
        if op == "add":
            return rs + rt
        elif op == "sub":
            return rs - rt
        elif op == "and":
            return rs & rt
        elif op == "or":
            return rs | rt
        elif op == "slt":
            return 1 if rs < rt else 0
    elif op == "lw":
        rt = decoded_fields['rd']  # This will be the destination register
        base = registers["$1"]  # Base address in $1
        offset = 0  # Assuming offset is 0
        return memory.get(base + offset, 0)  # Load the value from memory
    return 0

# Function to Simulate Memory Access
def memory_access(decoded_fields, result, memory):
    op = decoded_fields['op']
    if op == "lw":
        return result  # The result is already loaded from memory
    return None  # No memory access for other ops

# Function to Write Back to Register
def write_back(decoded_fields, data, registers):
    if decoded_fields['op'] == "lw":
        registers[decoded_fields['rd']] = data  # Write loaded data into the register
    elif decoded_fields['op'] in ["add", "sub", "and", "or", "slt"]:
        registers[decoded_fields['rd']] = data  # Write result into the destination register

# Load the Assembly File
data_segment, instruction_memory = load_asm_file('inputs/test_code_1_mips_sim.asm')

# Load Data into Memory
for label, value in data_segment.items():
    memory[data_segment_address] = value
    registers["$1"] = data_segment_address  # Store the address in $1
    data_segment_address += 4

# Simulation Loop
while pc < 0x00400000 + len(instruction_memory) * 4:  # Run until all instructions are executed
    print(f"PC: {hex(pc)}")
    print(f"Executing: {instruction_memory[(pc - 0x00400000) // 4]}")
    try:
        binary = translate_assembly_to_binary(instruction_memory[(pc - 0x00400000) // 4])
        print(f"Binary: {binary}")

        # Fetch, Decode, Execute, Memory, Write-Back
        fetched_instruction = instruction_fetch(pc, instruction_memory)
        decoded_fields = instruction_decode(fetched_instruction)
        result = execute(decoded_fields, registers)
        data = memory_access(decoded_fields, result, memory)
        write_back(decoded_fields, data or result, registers)

        pc += 4  # Increment PC for the next instruction

        print(f"Registers: {registers}")
        print(f"Memory: {memory}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        break  # Exit the loop on error

# Output Final State of Registers and Memory
print("Final Registers:", registers)
print("Final Memory:", memory)
