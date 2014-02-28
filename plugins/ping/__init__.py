from irc.irc import *
from plugins.BasePlugin import *

class Plugin(BasePlugin):

	name=""
	author=""
	description=""
	connection=None

	def ping(self, data):

		dest = ""
		message = data["message"]

		if message.destination == self.connection.config.nick:
			dest = message.sender.nick
		else:
			dest = message.destination


		msg = IRCPrivateMessage(dest, "%s: pong!" % message.sender.nick)
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
		self.name = "ping"
		self.author = "Mischa-Alff"
		self.description = "A simple ping-pong plugin."

		self.connection = kwargs.get("connection", None)

		self.commands.append(Command(self.ping, [r"%%nick%%"], ["ping","Ping","PING"]))

		super(Plugin, self).__init__(**kwargs)