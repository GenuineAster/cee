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
        self.name = "golf"
        self.author = "Mischa-Alff"
        self.description = "A C++ golf plugin using clang++."

        self.compiler_command = [
            "clang++",
            "-std=c++11",
            "-w",
            "-fmessage-length=0",
            "-ftemplate-depth-128",
            "-fno-elide-constructors",
            "-fstack-protector-all"
        ]

        super(Plugin, self).__init__(**kwargs)

        self.commands.append(
            plugins.BasePlugin.Command(
                self.curly_brace_snippet, ["%%prefix%%golf"], ["{"],
                {
                    "prefix_files": ["files/template.cpp", "files/golf.hpp"],
                    "suffix_files": [],
                    "lang_extension": "golf.cpp"
                }
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.stream_snippet, ["%%prefix%%golf"], ["<<"],
                {
                    "prefix_files": ["files/template.cpp", "files/golf.hpp"],
                    "suffix_files": [],
                    "lang_extension": "golf.cpp"
                }
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["%%prefix%%golf"], [""],
                {
                    "prefix_files": ["files/template.cpp", "files/golf.hpp"],
                    "suffix_files": [],
                    "lang_extension": "golf.cpp"
                }
            )
        )
