import plugins.BasePlugin
import plugins.CompilerPlugin


class Plugin(plugins.CompilerPlugin.CompilerPlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def curly_brace_snippet(self, data, extra_args):
        data["command"] = "int main()\n{" + data["command"]
        print data
        return self.snippet(data, extra_args)

    def stream_snippet(self, data, extra_args):
        data["command"] = " cout <<" + data["command"] + "; }"
        print data
        return self.curly_brace_snippet(data, extra_args)

    def __init__(self, **kwargs):
        self.name = "clang"
        self.author = "Mischa-Alff"
        self.description = "A C++ evaluation plugin using clang++ and SFML"

        self.compiler_command = [
            "clang++",
            "-g",
            "-Wall",
            "-std=c++1y",
            "-fmessage-length=0",
            "-ftemplate-depth-128",
            "-fno-elide-constructors",
            "-fstrict-aliasing",
            "-fstack-protector-all",
            "-lsfml-graphics",
            "-lsfml-audio",
            "-lsfml-network",
            "-lsfml-window",
            "-lsfml-system"
        ]

        super(Plugin, self).__init__(**kwargs)

        self.commands.append(
            plugins.BasePlugin.Command(
                self.curly_brace_snippet, ["%%prefix%%"], ["sfml {", "sfml{"],
                {
                    "prefix_files": ["files/template.cpp", "files/sfml.hpp"],
                    "suffix_files": [],
                    "lang_extension": "cpp"
                }
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.stream_snippet, ["%%prefix%%"], ["sfml<<", "sfml <<"],
                {
                    "prefix_files": ["files/template.cpp", "files/sfml.hpp"],
                    "suffix_files": [],
                    "lang_extension": "cpp"
                }
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["%%prefix%%"], ["sfml"],
                {
                    "prefix_files": ["files/template.cpp", "files/sfml.hpp"],
                    "suffix_files": [],
                    "lang_extension": "cpp"
                }
            )
        )
