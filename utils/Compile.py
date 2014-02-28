class CompilerException(Exception):
	error = None

	def __init__(self, error):
		self.error = error
