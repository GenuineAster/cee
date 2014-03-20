import plugins.InterpreterPlugin


class Plugin(plugins.InterpreterPlugin.InterpreterPlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def py_snippet(self, data, extra_args):
        data["command"] = data["command"].replace(";;", "\n")
        return self.snippet(data, extra_args)

    def __init__(self, **kwargs):
        self.name = "python"
        self.author = "Mischa-Alff"
        self.description = "A Python evaluation plugin."

        self.interpreter_command = ["/usr/bin/python2"]

        super(Plugin, self).__init__(**kwargs)

        self.commands.append(
            plugins.BasePlugin.Command(
                self.py_snippet, ["%%prefix%%python2"], [""],
                {
                    "lang_extension": "py"
                }
            )
        )

        self.commands.append(
            plugins.BasePlugin.Command(
                self.py_snippet, ["%%prefix%%py2"], [""],
                {
                    "lang_extension": "py"
                }
            )
        )
