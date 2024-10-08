.data
    x: .word 8
    y: .word 12

.text
    lw $t0, x
    lw $t1, y
    slt $t2, $t0, $t1  # If $t0 < $t1, $t2 = 1
    beq $t2, $zero, greater_case
    addi $t3, $t0, 5
    j end_case

greater_case:
    addi $t3, $t1, 5

end_case:
    sub $t4, $t3, $t0
