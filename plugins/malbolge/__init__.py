import plugins.InterpreterPlugin


class Plugin(plugins.InterpreterPlugin.InterpreterPlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def __init__(self, **kwargs):
        self.name = "malbolge"
        self.author = "Mischa-Alff"
        self.description = "A Malbolge evaluation plugin."

        self.interpreter_command = ["/usr/bin/python2", "/usr/bin/malbolge.py"]

        super(Plugin, self).__init__(**kwargs)

        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["%%prefix%%"], ["malbolge"],
                {
                    "lang_extension": "mbs"
                }
            )
        )

        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["%%prefix%%"], ["mbs"],
                {
                    "lang_extension": "mbs"
                }
            )
        )
