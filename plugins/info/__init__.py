from irc.irc import *
from plugins.BasePlugin import *

class Plugin(BasePlugin, object):

	name=None
	author=None
	description=None
	connection=None

	def source(self, data):

		dest = ""
		message = data["message"]

		if message.destination == self.connection.config.nick:
			dest = message.sender.nick
		else:
			dest = message.destination


		msg = IRCPrivateMessage(dest, "%s: https://github.com/Mischa-Alff/cee" % message.sender.nick)
		self.connection.send_message(msg)
		return True

	def handle_call(self, message):
		for command in self.commands:
			data = command.is_called(message, self.connection)
			if data is False:
				continue

			return command.function(data)
		return False



	def __init__(self, **kwargs):
		self.name = "info"
		self.author = "Mischa-Alff"
		self.description = "This plugin is used for getting info on this instance of cee."

		self.connection = kwargs.get("connection", None)

		self.commands = []

		self.commands.append(Command(self.source, [r"%%nick%%"], ["source"]))
