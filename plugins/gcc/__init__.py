import plugins.BasePlugin
import plugins.CompilerPlugin


class Plugin(plugins.CompilerPlugin.CompilerPlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def curly_brace_snippet(self, data, extra_args):
        data["command"] = "int main()\n{" + data["command"]
        return self.snippet(data, extra_args)

    def stream_snippet(self, data, extra_args):
        data["command"] = " cout <<" + data["command"] + "; }"
        return self.curly_brace_snippet(data, extra_args)

    def __init__(self, **kwargs):
        self.name = "gcc"
        self.author = "Mischa-Alff"
        self.description = "A C compiler plugin using gcc."

        self.compiler_command = [
            "gcc",
            "-std=c11",
            "-w",
            "-fmessage-length=0",
            "-fstack-protector-all"
        ]

        super(Plugin, self).__init__(**kwargs)

        self.commands.append(
            plugins.BasePlugin.Command(
                self.curly_brace_snippet, ["%%prefix%%"], ["gcc {", "gcc{"],
                {
                    "prefix_files": ["files/template.c"],
                    "suffix_files": [],
                    "lang_extension": "gcc.c"
                }
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.stream_snippet, ["%%prefix%%"], ["gcc<<", "gcc <<"],
                {
                    "prefix_files": ["files/template.c"],
                    "suffix_files": [],
                    "lang_extension": "gcc.c"
                }
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["%%prefix%%"], ["gcc"],
                {
                    "prefix_files": ["files/template.c"],
                    "suffix_files": [],
                    "lang_extension": "gcc.c"
                }
            )
        )
