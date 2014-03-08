import irc
import plugins.BasePlugin


class Plugin(plugins.BasePlugin.BasePlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def reload(self, data):

        dest = ""
        message = data["message"]

        if message.destination == self.connection.config.nick:
            dest = message.sender.nick
        else:
            dest = message.destination

        plugin_manager = data["plugin_manager"]

        plugin_manager.plugins = []
        plugin_manager.get_plugins()
        plugin_manager.load_plugins()

        msg = irc.IRCPrivateMessage(
            dest,
            "%s: reloaded." % message.sender.nick
        )
        self.connection.send_message(msg)
        return True

    def handle_call(self, message, **kwargs):
        self.connection = kwargs.get("connection", None)
        for command in self.commands:
            data = command.is_called(message, self.connection)
            if data is False:
                continue
            data["plugin_manager"] = kwargs.get("plugin_manager", None)
            return command.function(data)
        return False

    def __init__(self, **kwargs):
        self.name = "plugin_manager"
        self.author = "Mischa-Alff"
        self.description = "This plugin allows cee modify plugins on-the-fly."

        self.connection = kwargs.get("connection", None)

        self.commands = []

        self.commands.append(
            plugins.BasePlugin.Command(
                self.reload, [r"%%nick%%"], ["reload"]
            )
        )
