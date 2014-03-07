from irc import *
from plugins.BasePlugin import *

class Plugin(BasePlugin, object):

	name=None
	author=None
	description=None
	connection=None

	def join(self, data):

		dest = ""
		message = data["message"]

		if message.destination == self.connection.config.nick:
			dest = message.sender.nick
		else:
			dest = message.destination

		channels = data.get("command", "")

		channels.lstrip()
		channels.rstrip()
		channels = channels.split()[1]

		self.connection.join_channels(channels)
		return True

	def handle_call(self, message, **kwargs):
		self.connection = kwargs.get("connection", None)
		for command in self.commands:
			data = command.is_called(message, self.connection)
			if data is False:
				continue

			return command.function(data)
		return False



	def __init__(self, **kwargs):
		self.name = "irc_commands"
		self.author = "Mischa-Alff"
		self.description = "This plugin allows cee to execute certain IRC commands."

		self.connection = kwargs.get("connection", None)

		self.commands = []

		self.commands.append(Command(self.join, [r"%%nick%%"], ["join","Join","JOIN"]))

		#super(Plugin, self).__init__(**kwargs)
