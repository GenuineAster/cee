import plugins.BasePlugin
import plugins.CompilerPlugin


class Plugin(plugins.CompilerPlugin.CompilerPlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def curly_brace_snippet(self, data, extra_args):
        data["command"] = "int main()\n" + data["command"]
        return self.snippet(data, extra_args)

    def stream_snippet(self, data, extra_args):
        data["command"] = "{ cout " + data["command"] + "; }"
        return self.curly_brace_snippet(data, extra_args)

    def __init__(self, **kwargs):
        self.name = "g++"
        self.author = "Mischa-Alff"
        self.description = "A C++ evaluation plugin using g++."

        self.compiler_command = [
            "g++",
            "-Wall",
            "-std=c++11",
            "-finput-charset=UTF-8",
            "-fno-use-linker-plugin",
            "-fmessage-length=0",
            "-ftemplate-depth-128",
            "-fno-merge-constants",
            "-fno-nonansi-builtins",
            "-fno-gnu-keywords",
            "-fno-elide-constructors",
            "-fstrict-aliasing",
            "-fstack-protector-all"
        ]

        super(Plugin, self).__init__(**kwargs)

        self.commands.append(
            plugins.BasePlugin.Command(
                self.curly_brace_snippet, ["%%nick%%", "g++", ""], ["{"],
                {
                    "prefix_files": ["files/template.cpp"],
                    "suffix_files": [],
                    "lang_extension": "cpp"
                }
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.stream_snippet, ["%%nick%%", "g++", ""], ["<<"],
                {
                    "prefix_files": ["files/template.cpp"],
                    "suffix_files": [],
                    "lang_extension": "cpp"
                }
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["g++"], [""],
                {
                    "prefix_files": ["files/template.cpp"],
                    "suffix_files": [],
                    "lang_extension": "cpp"
                }
            )
        )
