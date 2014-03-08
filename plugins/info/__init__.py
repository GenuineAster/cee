import irc
import plugins.BasePlugin


class Plugin(plugins.BasePlugin.BasePlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def source(self, data, **kwargs):

        dest = ""
        message = data["message"]

        if message.destination == self.connection.config.nick:
            dest = message.sender.nick
        else:
            dest = message.destination

        msg = irc.IRCPrivateMessage(
            dest,
            "%s: https://github.com/Mischa-Alff/cee" % message.sender.nick
        )
        self.connection.send_message(msg)
        return True

    def plugins(self, data, **kwargs):

        dest = ""
        message = data["message"]

        if message.destination == self.connection.config.nick:
            dest = message.sender.nick
        else:
            dest = message.destination

        plugin_manager = kwargs.get("plugin_manager", [])
        plugins = plugin_manager.plugins[:]
        plugin_names = []

        command = data["command"].lstrip("plugins")
        command = command.lstrip()
        command = command.rstrip()

        for plugin in plugins:
            plugin_names.append(plugin.data["name"])
            if plugin.data["name"] == command:
                commands = []
                for com in plugin.plugin_object.commands:
                    commands.append([com.prefixes, com.words])

                msg = irc.IRCPrivateMessage(dest, "%s" % commands)
                self.connection.send_message(msg)
                return True

        msg = irc.IRCPrivateMessage(dest, "%s" % plugin_names)
        self.connection.send_message(msg)
        return True

    def handle_call(self, message, **kwargs):
        self.connection = kwargs.get("connection", None)
        for command in self.commands:
            data = command.is_called(message, self.connection)
            if data is False:
                continue

            data["plugin_manager"] = kwargs.get("plugin_manager", None)
            return command.function(data, **kwargs)
        return False

    def __init__(self, **kwargs):
        self.name = "info"
        self.author = "Mischa-Alff"
        self.description = "This plugin is used for getting info on \
            this instance of cee."

        self.connection = kwargs.get("connection", None)

        self.commands = []

        self.commands.append(
            plugins.BasePlugin.Command(
                self.source, [r"%%nick%%"], ["source"]
            )
        )
        self.commands.append(
            plugins.Baseplugin.Command(
                self.plugins, [r"%%nick%%"], ["plugins"]
            )
        )
