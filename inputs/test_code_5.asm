.data
    limit: .word 10

.text
    li $t0, 0           # Initialize counter to 0
    lw $t1, limit       # Load limit into $t1
loop_check:
    bge $t0, $t1, end_count # If counter >= limit, exit loop
    addi $t0, $t0, 1    # Increment counter
    j loop_check        # Repeat the loop
end_count:
    # Final counter value is in $t0
