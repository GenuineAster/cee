from irc.irc import *
import re

class Command(object):
	prefixes = []
	words = []
	function = None

	def find_prefix(self, message, connection):
		for prefix in self.prefixes:
			findstring = re.sub("%%nick%%", connection.config.nick, prefix)
			if message.message.startswith(findstring):
				return findstring
		return None

	def is_called(self, message, connection):
		prefix = self.find_prefix(message, connection)
		if prefix is None:
			return False

		command = message.message[len(prefix):]

		command = command.lstrip()
		command = command.lstrip(":")
		command = command.lstrip(",")
		command = command.lstrip()


		for word in self.words:
			if command.startswith(word):
				return {
					"prefix":prefix, 
					"word":word,
					"command":command,
					"connection":connection,
					"message":message
				}

		return False



	def __init__(self, func, prefixes, words):
		self.function = func
		self.prefixes = prefixes
		self.words = words


class BasePlugin(object):
	name = ""
	author = ""
	description = ""
	commands = []

	connection = None

	def handle_call(self, message):
		raise NotImplementedError("Please implement handle_call in plugin " % name)

	def __init__(self, **kwargs):
		self.connection = kwargs.get("connection", None)
