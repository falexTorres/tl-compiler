	.data
newline:
	.asciiz	"\n"

	.text
	.globl	main

main:
	li $t0, 0
	sw $t0, 0($fp)
	li $v0, 5
	syscall
	add $t0, $v0, $zero
	sw $t0, 0($fp)
	li $t0, 2
	sw $t0, -4($fp)
	lw $t1, -4($fp)
	lw $t2, 0($fp)
	mulo $t0, $t1, $t2
	sw $t0, -8($fp)
	li $v0, 1
	lw $t1, -8($fp)
	add $a0, $t1, $zero
	syscall
	li $v0, 4
	la $a0, newline
	syscall
	li $v0, 10
	syscall
