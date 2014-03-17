import plugins.InterpreterPlugin


class Plugin(plugins.InterpreterPlugin.InterpreterPlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def __init__(self, **kwargs):
        self.name = "php"
        self.author = "Mischa-Alff"
        self.description = "A PHP evaluation plugin."

        self.interpreter_command = ["/usr/bin/php"]

        super(Plugin, self).__init__(**kwargs)

        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["%%prefix%%php", ""], [""],
                {
                    "lang_extension": "php"
                }
            )
        )
