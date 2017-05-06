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
	li $v0, 5
	syscall
	add $t0, $v0, $zero
	sw $t0, 0($fp)
	li $t0, 0
	sw $t0, -8($fp)
	lw $t1, -8($fp)
	add $t0, $t1, $zero
	sw $t0, -4($fp)
	j Block1

Block1:
	lw $t1, -4($fp)
	lw $t2, -4($fp)
	mulo $t0, $t1, $t2
	sw $t0, -12($fp)
	lw $t1, -12($fp)
	lw $t2, 0($fp)
	sle $t0, $t1, $t2
	sw $t0, -16($fp)
	lw $t0, -16($fp)
	bne $t0, $zero, Block3
	j Block2

Block3:
	li $t0, 1
	sw $t0, -20($fp)
	lw $t1, -4($fp)
	lw $t2, -20($fp)
	add $t0, $t1, $t2
	sw $t0, -24($fp)
	lw $t1, -24($fp)
	add $t0, $t1, $zero
	sw $t0, -4($fp)
	j Block1

Block2:
	lw $t1, -4($fp)
	lw $t2, -20($fp)
	sub $t0, $t1, $t2
	sw $t0, -28($fp)
	lw $t1, -28($fp)
	add $t0, $t1, $zero
	sw $t0, -4($fp)
	li $v0, 1
	lw $t1, -4($fp)
	add $a0, $t1, $zero
	syscall
	li $v0, 4
	la $a0, newline
	syscall
	li $v0, 10
	syscall
