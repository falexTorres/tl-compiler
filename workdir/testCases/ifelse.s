	.data
newline:
	.asciiz	"\n"

	.text
	.globl	Block0

Block0:
	li $t0, 0
	sw $t0, 0($fp)
	li $t0, 0
	sw $t0, -4($fp)
	li $t0, 0
	sw $t0, -8($fp)
	li $v0, 5
	syscall
	add $t0, $v0, $zero
	sw $t0, 0($fp)
	li $t0, 0
	sw $t0, -12($fp)
	lw $t1, -12($fp)
	add $t0, $t1, $zero
	sw $t0, -4($fp)
	j Block1

Block1:
	lw $t1, -4($fp)
	lw $t2, -4($fp)
	mulo $t0, $t1, $t2
	sw $t0, -16($fp)
	lw $t1, -16($fp)
	lw $t2, 0($fp)
	sle $t0, $t1, $t2
	sw $t0, -20($fp)
	lw $t0, -20($fp)
	bne $t0, $zero, Block2
	j Block3

Block2:
	li $t0, 1
	sw $t0, -24($fp)
	lw $t1, -4($fp)
	lw $t2, -24($fp)
	add $t0, $t1, $t2
	sw $t0, -28($fp)
	lw $t1, -28($fp)
	add $t0, $t1, $zero
	sw $t0, -4($fp)
	li $t0, 5
	sw $t0, -32($fp)
	lw $t1, -32($fp)
	add $t0, $t1, $zero
	sw $t0, 0($fp)
	j Block4

Block4:
	li $t0, 100
	sw $t0, -40($fp)
	lw $t1, -40($fp)
	add $t0, $t1, $zero
	sw $t0, -8($fp)
	li $v0, 10
	syscall

Block3:
	li $t0, 2
	sw $t0, -36($fp)
	lw $t1, -36($fp)
	add $t0, $t1, $zero
	sw $t0, 0($fp)
	j Block4
