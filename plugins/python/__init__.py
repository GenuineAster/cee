import plugins.InterpreterPlugin


class Plugin(plugins.InterpreterPlugin.InterpreterPlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def __init__(self, **kwargs):
        self.name = "python"
        self.author = "Mischa-Alff"
        self.description = "A Python evaluation plugin."

        self.interpreter_command = ["/usr/bin/python"]

        super(Plugin, self).__init__(**kwargs)

        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["%%prefix%%python"], [""],
                {
                    "lang_extension": "py"
                }
            )
        )

        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["%%prefix%%py"], [""],
                {
                    "lang_extension": "py"
                }
            )
        )
