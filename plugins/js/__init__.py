import plugins.InterpreterPlugin


class Plugin(plugins.InterpreterPlugin.InterpreterPlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def __init__(self, **kwargs):
        self.name = "js"
        self.author = "Mischa-Alff"
        self.description = "A JavaScript evaluation plugin."

#        self.interpreter_command = ["/usr/bin/spidermonkey-1.7", "-f"]
        self.interpreter_command = ["/usr/bin/js24", "-f"]

        super(Plugin, self).__init__(**kwargs)

        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["%%prefix%%"], ["js"],
                {
                    "lang_extension": "js"
                }
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["%%prefix%%"], ["javascript"],
                {
                    "lang_extension": "js"
                }
            )
        )
