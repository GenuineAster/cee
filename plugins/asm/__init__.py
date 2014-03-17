import os
import plugins.CompilerPlugin
import easyprocess
import irc
import plugins.BasePlugin
from utils.Compile import CompilerException
import platform


class Plugin(plugins.CompilerPlugin.CompilerPlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def assemble_code(self, filename, output, assembler):
        assembler_output_raw = ""
        assembler_output = []
        assembler_command_temp = assembler[:]
        if platform.system() == "Linux":
            if os.uname()[4] == 'x86_64':
                assembler_command_temp.append("-f")
                assembler_command_temp.append("elf64")
            elif os.uname()[4] == 'i686':
                assembler_command_temp.append("-f")
                assembler_command_temp.appent("elf32")

        assembler_command_temp.append(filename)
        assembler_command_temp.append("-o%s.o" % output)
        assembler_process_data = easyprocess.EasyProcess(
            assembler_command_temp
        ).call(timeout=30)
        assembler_output_raw = (
            assembler_process_data.stdout + assembler_process_data.stderr
        )

        if assembler_output_raw:
            assembler_output = assembler_output_raw.split("\n")
            for i in range(len(assembler_output)):
                assembler_output[i] = assembler_output[i].split(" ", 1)[1]

            raise CompilerException(
                "Assembler error: " + assembler_output[0]
            )

            return False

        else:
            return True

    def link(self, data, output):
        linker = "gcc"
        if "_start" in data["command"]:
            linker = "ld"
        elif "main" in data["command"]:
            linker = "gcc"

        linker_command = [linker, "%s.o" % output, "-o", output]
        linker_process_data = easyprocess.EasyProcess(
            linker_command
        ).call(timeout=30)

        linker_output_raw = (
            linker_process_data.stdout + linker_process_data.stderr
        )

        if linker_output_raw:
            linker_output = linker_output_raw.split("\n")
            raise CompilerException(
                "Linker error:" + linker_output[0]
            )
            return False

        else:
            return True

    def snippet(self, output, assembler, data):
        message = data["message"]

        if message.destination == self.connection.config.nick:
            dest = message.sender.nick
        else:
            dest = message.destination

        try:
            os.remove("files/output/code.asm")
            os.remove(output)
        except OSError as e:
            pass

        asm_file = open("files/output/code.asm", "w+")
        asm_file.write(data["command"].replace("\\n", "\n"))
        asm_file.flush()
        asm_file.close()

        try:
            self.assemble_code(
                "files/output/code.asm",
                output,
                assembler
            )
            self.link(data, output)

        except CompilerException as e:
            self.connection.send_message(
                irc.IRCPrivateMessage(dest, e.error)
            )
        else:
            self.connection.send_message(
                irc.IRCPrivateMessage(dest, self.run("files/output/output"))
            )

        return True

    def nasm(self, data, extra_args={}):
        output = "files/output/output"
        return self.snippet(output, ["nasm"], data)

    def yasm(self, data, extra_args={}):
        output = "files/output/output"
        return self.snippet(output, ["yasm", "-pnasm"], data)

    def tasm(self, data, extra_args={}):
        output = "files/output/output"
        return self.snippet(output, ["yasm", "-ptasm"], data)

    def gas(self, data, extra_args={}):
        output = "files/output/output"
        return self.snippet(output, ["yasm", "-pgas"], data)

    def __init__(self, **kwargs):
        self.name = "asm"
        self.author = "Mischa-Alff"
        self.description = "A asm evaluation plugin using several assemblers."

        super(Plugin, self).__init__(**kwargs)

        self.commands.append(
            plugins.BasePlugin.Command(
                self.nasm, ["nasm"], [""]
            )
        )

        self.commands.append(
            plugins.BasePlugin.Command(
                self.yasm, ["yasm"], [""]
            )
        )

        self.commands.append(
            plugins.BasePlugin.Command(
                self.tasm, ["tasm"], [""]
            )
        )

        self.commands.append(
            plugins.BasePlugin.Command(
                self.gas, ["gas"], [""]
            )
        )
