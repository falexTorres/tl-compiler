

class MipsSource:
	@staticmethod
	def getMipsSource(cfg):
		mips_source = "\t.data\nnewline:\n\t.asciiz\t\"\\n\"\n"
		mips_source += "\n\t.text\n\t.globl\tmain\n"
		mips_source += "main:\n\tli $fp, 0x7ffffffc\n"
		get_instructions = False
		for line in cfg.split('\n'):
			block_in_line = "Block" in line and ("<TR><TD border=\"1\" colspan=\"3\">Block") in line
			if get_instructions == True:
				if "</TABLE> >, ];" in line:
					get_instructions = False
					continue
				mips_source += "\t" + line.strip().replace('<TR><TD>', '').replace('</TD></TR>', '') + "\n"
			if block_in_line:
				mips_source += "\n" + MipsSource.getBlockName(line.strip()) + ":\n"
				get_instructions = True

		return mips_source

	@staticmethod
	def getBlockName(cfg_line):
		return cfg_line.split(' ')[0]

	@staticmethod
	def writeAssemblyFile(source, base_name):
		with open(base_name + '.s', 'w') as output:
			output.write(source)