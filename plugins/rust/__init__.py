import plugins.BasePlugin
import plugins.CompilerPlugin


class Plugin(plugins.CompilerPlugin.CompilerPlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def curly_brace_snippet(self, data, extra_args):
        data["command"] = "fn main()\n{" + data["command"]
        print data
        return self.snippet(data, extra_args)

    def stream_snippet(self, data, extra_args):
        data["command"] = " println!(" + data["command"] + "); }"
        print data
        return self.curly_brace_snippet(data, extra_args)

    def __init__(self, **kwargs):
        self.name = "clang"
        self.author = "Mischa-Alff"
        self.description = "A C++ evaluation plugin using clang++."

        self.compiler_command = [
            "rustc",
            "--crate-type", "bin",
            "--crate-name", "cee",
#            "-Wall",
#            "-std=c++1y",
#            "-trigraphs",
#            "-g",
#            "-fmessage-length=0",
#            "-ftemplate-depth-128",
#            "-fno-elide-constructors",
#            "-fstrict-aliasing",
#            "-fstack-protector-all"
        ]

        super(Plugin, self).__init__(**kwargs)

        self.commands.append(
            plugins.BasePlugin.Command(
                self.curly_brace_snippet, ["%%prefix%%"], ["rs {", "rs{"],
                {
                    "prefix_files": [],
                    "suffix_files": [],
                    "lang_extension": "rs"
                }
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.stream_snippet, ["%%prefix%%"], ["rs !", "rs!"],
                {
                    "prefix_files": [],
                    "suffix_files": [],
                    "lang_extension": "rs"
                }
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["%%prefix%%"], ["rs"],
                {
                    "prefix_files": [],
                    "suffix_files": [],
                    "lang_extension": "rs"
                }
            )
        )
