import irc  # noqa
import plugins.BasePlugin


class Plugin(plugins.BasePlugin.BasePlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def join(self, data):

        channels = data.get("command", "")

        channels.lstrip()
        channels.rstrip()
        channels = channels.split()
        if len(channels) < 2:
            return True

        channels = channels[1]

        self.connection.join_channels(channels)
        return True

    def part(self, data):

        message = data["message"]
        channels = data.get("command", "")

        channels.lstrip()
        channels.rstrip()
        channels = channels.split()
        if len(channels) < 2:
            print(channels)
            self.connection.part_channel(message.destination)
        else:
            channels = channels[1]
            self.connection.part_channels(channels)

        return True

    def handle_call(self, message, **kwargs):
        self.connection = kwargs.get("connection", None)
        for command in self.commands:
            data = command.is_called(message, self.connection)
            if not data:
                continue

            return command.function(data)
        return False

    def __init__(self, **kwargs):
        self.name = "irc_commands"
        self.author = "Mischa-Alff"
        self.description = "This plugin allows cee to execute \
            certain IRC commands."

        self.connection = kwargs.get("connection", None)

        self.commands = []

        self.commands.append(
            plugins.BasePlugin.Command(
                self.join, [r"%%nick%%"], ["join", "Join", "JOIN"]
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.part, [r"%%nick%%"], ["part", "Part", "PART"]
            )
        )

        #super(Plugin, self).__init__(**kwargs)
