import os
import sys
import string
import time
import re
from kitchen.text.converters import to_unicode, to_bytes
from easyprocess import EasyProcess
from irc import *
from plugins.BasePlugin import *
from utils.Compile import *
from sandbox import *

compiler_clang = ["clang++","-Wall","-std=c++11"];


system, machine = os.uname()[0], os.uname()[4]

class MiniSandbox(SandboxPolicy, Sandbox):
	sc_table = None
	# white list of essential linux syscalls for statically-linked C programs
	sc_safe = dict(i686=set([0, 3, 4, 19, 45, 54, 90, 91, 122, 125, 140,
		163, 192, 197, 224, 243, 252, ]), x86_64=set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330]), )
	# result code translation table
	result_name = dict((getattr(Sandbox, 'S_RESULT_%s' % r), r) for r in
		('PD', 'OK', 'RF', 'RT', 'TL', 'ML', 'OL', 'AT', 'IE', 'BP'))

	def __init__(self, *args, **kwds):
		# initialize table of system call rules
		self.sc_table = dict()
		if machine == 'x86_64':
			for (mode, abi) in ((0, 'x86_64'), (1, 'i686'), ):
				for scno in MiniSandbox.sc_safe[abi]:
					self.sc_table[(scno, mode)] = self._CONT
		else:  # i686
			for scno in MiniSandbox.sc_safe[machine]:
				self.sc_table[scno] = self._CONT
		# initialize as a polymorphic sandbox-and-policy object
		SandboxPolicy.__init__(self)
		Sandbox.__init__(self, *args, **kwds)
		self.policy = self  # apply local policy rules

	def probe(self):
		# add custom entries into the probe dict
		d = Sandbox.probe(self, False)
		d['cpu'] = d['cpu_info'][0]
		d['mem'] = d['mem_info'][1]
		d['result'] = MiniSandbox.result_name.get(self.result, 'NA')
		return d

	def __call__(self, e, a):
		# handle SYSCALL/SYSRET events with local rules
		if e.type in (S_EVENT_SYSCALL, S_EVENT_SYSRET):
			scinfo = (e.data, e.ext0) if machine == 'x86_64' else e.data
			rule = self.sc_table.get(scinfo, self._KILL_RF)
			#print({sc_table})
			return rule(e, a)
		# bypass other events to base class
		return SandboxPolicy.__call__(self, e, a)

	def _CONT(self, e, a):  # continue
		a.type = S_ACTION_CONT
		return a

	def _KILL_RF(self, e, a):  # restricted func.
		a.type, a.data = S_ACTION_KILL, S_RESULT_RF
		return a

class out(str, object):
	def write(string):
		self += string + "\n"

class Plugin(BasePlugin, object):

	name=None
	author=None
	description=None
	connection=None

	def compile_code(self, filename, output):
		compiler_output_raw = ""
		compiler_output = []
		compiler_command_temp = compiler_clang[:]
		compiler_command_temp.append(filename)
		compiler_command_temp.append("-o%s" % output)
		compiler_process_data = EasyProcess(compiler_command_temp).call(timeout=30)
		compiler_output_raw = compiler_process_data.stdout + compiler_process_data.stderr

		if compiler_output_raw:
			compiler_output = compiler_output_raw.split("\n")
			compiler_output = filter(lambda x:re.search(r"(error|warning):", x), compiler_output)
			for i in range(len(compiler_output)):
				compiler_output[i] = compiler_output[i].split(" ", 1)[1]

			raise CompilerException(compiler_output[0])

			return False

		else:
			return True

	def run(self, filename):
		program_output_raw  = ""
		message_string = ""

		output = open("/tmp/cee_output", "w+")

		cookbook = {
			'args': os.path.join(os.getcwd(),filename),               # targeted program
			'stdin': sys.stdin,             # input to targeted program
			'stdout': output,           # output from targeted program
			'stderr': output,           # error from targeted program
			'quota': dict(wallclock=30000,  # 30 sec
						  cpu=20000,         # 2 sec
						  memory=100000000, # 100 MB
						  disk=1048576)}    # 1 MB
		# create a sandbox instance and execute till end

		try:
			msb = MiniSandbox(**cookbook)
			msb.run()
		except ValueError as e:
			return "<killed> ( recieved fork attempt )"
		else:
			# verbose statistics
			program_output_data = msb.probe()

			output.flush()
			output.close()
			output = open("/tmp/cee_output", "r")

			program_output_raw = output.read()

			temp = program_output_raw.replace("\r", "")
			program_output = temp.split("\n")
			message_string = program_output[0]
			message_string.rstrip()

			message_string = to_bytes(message_string)

			print(program_output_data.get("result", False))

			if program_output_data.get("result", False) is "TL":
				message_string = "<killed> ( timed out )"
			elif program_output_data.get("result", False) is "RF":
				message_string = "<killed> ( restricted function used )"
			else:
				if program_output[0]:

					if len(program_output) > 1:
						message_string = to_bytes(message_string + " [+%d deleted lines]" % (len(program_output)-1))

					max_msg_len = 400-len("[+nnn deleted bytes]")
					if len(message_string) > max_msg_len:
						message_string = message_string[:max_msg_len] + ("[+%d deleted bytes]" % (len(message_string)-max_msg_len))

				else:
					message_string = "<no output> ( return value was %d ) " % program_output_data.get("exitcode", -1)

			return message_string

	def snippet(self, data):
		message = data["message"]

		if message.destination == self.connection.config.nick:
			dest = message.sender.nick
		else:
			dest = message.destination

		sender = message.sender.nick
		msg  = message.message

		try:
			os.remove("files/code.cpp")
			os.remove("files/output")
		except OSError as e:
			pass

		cpp_template_file = open("files/template.cpp", "r")
		cpp_file = open("files/code.cpp", "w+")
		cpp_file.write(cpp_template_file.read())
		cpp_template_file.close()
		cpp_file.write("\n")
		cpp_file.write(data["command"])
		cpp_file.flush()
		cpp_file.close()

		try:
			self.compile_code("files/code.cpp", "files/output")
		except CompilerException as e:
			self.connection.send_message(IRCPrivateMessage(dest, e.error))
		else:
			self.connection.send_message(IRCPrivateMessage(dest, self.run("files/output")))

		return True

	def curly_brace_snippet(self, data):

		data["command"] = "int main()\n" + data["command"]
		return self.snippet(data)

	def stream_snippet(self, data):
		data["command"] = "{ cout " + data["command"] + "; }"
		return self.curly_brace_snippet(data)


	def handle_call(self, message, **kwargs):
		self.connection = kwargs.get("connection", None)
		for command in self.commands:
			data = command.is_called(message, self.connection)
			if data is False:
				continue

			return command.function(data)
		return False



	def __init__(self, **kwargs):
		self.name = "clang++"
		self.author = "Mischa-Alff"
		self.description = "A C++ evaluation plugin using clang++."

		self.connection = kwargs.get("connection", None)

		self.commands = []

		self.commands.append(Command(self.curly_brace_snippet, ["clang"], ["{"]))
		self.commands.append(Command(self.stream_snippet, ["clang"], ["<<"]))
		self.commands.append(Command(self.snippet, ["clang"], [""]))

