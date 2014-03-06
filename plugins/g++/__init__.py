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

compiler_command = ["g++","-Wall","-std=c++11"];

system, machine = os.uname()[0], os.uname()[4]

class MiniSandbox(SandboxPolicy, Sandbox):
	sc_table = None
	# white list of essential linux syscalls for statically-linked C programs
	sc_safe = dict(i686=set([0, 3, 4, 19, 45, 54, 90, 91, 122, 125, 140,
		163, 192, 197, 224, 243, 252, ]), x86_64=set(range(0, 331)), )
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
		compiler_command_temp = compiler_command[:]
		compiler_command_temp.append(filename)
		compiler_command_temp.append("-o%s" % output)
		compiler_process_data = EasyProcess(compiler_command_temp).call(timeout=30)
		compiler_output_raw = compiler_process_data.stdout

		if compiler_output_raw:
			print(to_bytes(to_unicode(compiler_output_raw)))
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
			'args': filename,               # targeted program
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
				message_string = "<killed>"
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
		self.name = "g++"
		self.author = "Mischa-Alff"
		self.description = "A C++ evaluation plugin using g++."

		self.connection = kwargs.get("connection", None)

		self.commands = []

		self.commands.append(Command(self.curly_brace_snippet, ["%%nick%%", "g++", ""], ["{"]))
		self.commands.append(Command(self.stream_snippet, ["%%nick%%", "g++", ""], ["<<"]))
		self.commands.append(Command(self.snippet, ["g++"], [""]))

		#super(Plugin, self).__init__(**kwargs)
