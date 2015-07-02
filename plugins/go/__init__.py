import plugins.BasePlugin
import plugins.CompilerPlugin


class Plugin(plugins.CompilerPlugin.CompilerPlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def curly_brace_snippet(self, data, extra_args):
        data["command"] = "func main()\n{" + data["command"]
        return self.snippet(data, extra_args)

    def __init__(self, **kwargs):
        self.name = "go
        self.author = "nekomune"
        self.description = "A go compiler plugin."

        self.compiler_command = [
            "go run"
        ]

        super(Plugin, self).__init__(**kwargs)

        default_param = {
            "prefix_files": ["files/template.go"],
            "suffix_files": [],
            "lang_extension": "go"
        }

        self.commands.append(plugins.BasePlugin.Command(
            self.curly_brace_snippet, ["%%prefix%%"], ["go {", "go{"], default_param
        ))
        self.commands.append(plugins.BasePlugin.Command(
            self.snippet, ["%%prefix%%"], ["go"], default_param
        ))
