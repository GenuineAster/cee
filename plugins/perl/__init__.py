import plugins.InterpreterPlugin


class Plugin(plugins.InterpreterPlugin.InterpreterPlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def __init__(self, **kwargs):
        self.name = "perl"
        self.author = "Mischa-Alff"
        self.description = "A Perl evaluation plugin."

        self.interpreter_command = ["/usr/bin/perl"]

        super(Plugin, self).__init__(**kwargs)

        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["%%prefix%%"], ["pl"],
                {
                    "lang_extension": "pl"
                }
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["%%prefix%%"], ["perl"],
                {
                    "lang_extension": "pl"
                }
            )
        )
