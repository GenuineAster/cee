import plugins.InterpreterPlugin


class Plugin(plugins.InterpreterPlugin.InterpreterPlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def __init__(self, **kwargs):
        self.name = "lua"
        self.author = "Mischa-Alff"
        self.description = "A Lua evaluation plugin."

        self.interpreter_command = ["/usr/bin/lua"]

        super(Plugin, self).__init__(**kwargs)

        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["%%prefix%%lua"], [""],
                {
                    "lang_extension": "lua"
                }
            )
        )
