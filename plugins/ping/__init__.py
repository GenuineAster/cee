import irc
import plugins.BasePlugin


class Plugin(plugins.BasePlugin.BasePlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def ping(self, data):

        dest = ""
        message = data["message"]

        if message.destination == self.connection.config.nick:
            dest = message.sender.nick
        else:
            dest = message.destination

        msg = irc.IRCPrivateMessage(dest, "%s: pong!" % message.sender.nick)
        self.connection.send_message(msg)
        return True

    def handle_call(self, message, **kwargs):
        self.connection = kwargs.get("connection", None)
        for command in self.commands:
            data = command.is_called(message, **kwargs)
            if not data:
                continue

            return command.function(data)
        return False

    def __init__(self, **kwargs):
        self.name = "ping"
        self.author = "Mischa-Alff"
        self.description = "A simple ping-pong plugin."

        self.connection = kwargs.get("connection", None)

        self.commands = []

        self.commands.append(
            plugins.BasePlugin.Command(
                self.ping, [r"%%nick%%"], ["ping", "Ping", "PING"]
            )
        )
