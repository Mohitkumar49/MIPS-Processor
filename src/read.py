   

def read_asm_file(file_path):
    """Read MIPS assembly code from a file and return it as a list of strings."""
    with open(file_path, 'r') as file:
        assembly_code = file.readlines()
    # Strip whitespace and newlines from each line
    assembly_code = [line.strip() for line in assembly_code if line.strip()]
    return assembly_code

if __name__ == "__main__":
    assembly_code = read_asm_file('inputs/test_code_1_mips_sim.asm')
    print("Assembly Code:")
    for line in assembly_code:
        print(line)
