import plugins.InterpreterPlugin


class Plugin(plugins.InterpreterPlugin.InterpreterPlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def py_snippet(self, data, extra_args):
        data["command"] = data["command"].replace(";;", "\n")
        return self.snippet(data, extra_args)

    def parse_output(self, message_string, program_output):
        found = [False, False]
        for line in program_output:
            if "traceback" in line.lower():
                found = [True, program_output.index(line)]

        if found[0]:
            found[1] += 1
            while found[1] < len(program_output):
                if program_output[found[1]][0] != " ":
                    message_string = program_output[found[1]]
                    break
                found[1] += 1

        message_string = self.strip_output(message_string, program_output)
        return message_string

    def __init__(self, **kwargs):
        self.name = "python"
        self.author = "Mischa-Alff"
        self.description = "A Python evaluation plugin."

        self.interpreter_command = ["/usr/bin/python"]

        super(Plugin, self).__init__(**kwargs)

        self.commands.append(
            plugins.BasePlugin.Command(
                self.py_snippet, ["%%prefix%%python"], [""],
                {
                    "lang_extension": "py"
                }
            )
        )

        self.commands.append(
            plugins.BasePlugin.Command(
                self.py_snippet, ["%%prefix%%py"], [""],
                {
                    "lang_extension": "py"
                }
            )
        )
