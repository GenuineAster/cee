import os
import sys
import string
import time
import re
from kitchen.text.converters import to_unicode, to_bytes
from easyprocess import EasyProcess
from irc.irc import *
from plugins.BasePlugin import *
from utils.Compile import *

compiler_command = ["g++","-Wall","-std=c++11"];


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
		compiler_output_raw = compiler_process_data.stderr

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

		program_output_data = EasyProcess(filename).call(timeout=30)
		program_output_raw = program_output_data.stdout
		temp = program_output_raw.replace("\r", "")
		program_output = temp.split("\n")
		message_string = program_output[0]
		message_string.rstrip()

		message_string = to_bytes(message_string)

		if program_output[0]:

			if len(program_output) > 1:
				message_string = to_bytes(message_string + " [+%d deleted lines]" % (len(program_output)-1))

			max_msg_len = 400-len("[+nnn deleted bytes]")
			if len(message_string) > max_msg_len:
				message_string = message_string[:max_msg_len] + ("[+%d deleted bytes]" % (len(message_string)-max_msg_len))

		else:
			message_string = "<no output> ( return value was %d ) " % program_output_data.return_code

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
