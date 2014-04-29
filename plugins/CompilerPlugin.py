import os
import sys
import re
from kitchen.text.converters import to_bytes
import easyprocess
import irc
import plugins.BasePlugin
from utils.Compile import CompilerException
import random
import plugins.MiniSandbox


class CompilerPlugin(plugins.BasePlugin.BasePlugin, object):

    name = None
    author = None
    description = None
    connection = None
    compiler_command = None
    out_flag = None

    def compile_code(self, filename, output):
        compiler_output_raw = ""
        compiler_output = []
        compiler_command_temp = self.compiler_command[:]
        compiler_command_temp.append("%s%s" % (self.out_flag, output))
        compiler_command_temp.append(filename)
        if "clang++" in compiler_command_temp:
            compiler_command_temp.append("-stdlib=libc++")
            compiler_command_temp.append("-lc++abi")
        compiler_process_data = easyprocess.EasyProcess(
            compiler_command_temp
        ).call(timeout=30)
        compiler_output_raw = (
            compiler_process_data.stdout +
            compiler_process_data.stderr
        )

        if compiler_output_raw:
            print(compiler_output_raw)
            compiler_output = compiler_output_raw.split("\n")
            compiler_output = filter(
                lambda x: re.search(r"(error|warning)", x),
                compiler_output
            )
            for i in range(len(compiler_output)):
                compiler_output[i] = compiler_output[i].split(" ", 1)[1]

            raise CompilerException(compiler_output[0])

            return False

        else:
            return True

    def run(self, filename):
        program_output_raw = ""
        message_string = ""

        output = open(
            "files/output/cee_output_%s" %
            re.sub('[^0-9a-zA-Z]+', '*', filename),
            "w+"
        )

        args = []
        if self.run_cmd:
            args.append(self.run_cmd)
        args.append(os.path.join(os.getcwd(), filename))

        cookbook = {
            'args': args,
            'stdin': sys.stdin,
            'stdout': output,
            'stderr': output,
            'quota': dict(
                wallclock=10000,
                cpu=5000,
                memory=100000000,
                disk=1048576
            )
        }

        try:
            msb = plugins.MiniSandbox.MiniSandbox(**cookbook)
            msb.run()
        except ValueError as e:
            print(e)
            return "<killed> ( recieved fork attempt )"
            output.flush()
            output.close()
        else:
            # verbose statistics
            program_output_data = msb.probe()

            output.flush()
            output.close()
            output = open(
                "files/output/cee_output_%s" %
                re.sub('[^0-9a-zA-Z]+', '*', filename),
                "r"
            )

            program_output_raw = output.read()

            temp = program_output_raw.replace("\r", "")
            program_output = temp.split("\n")
            message_string = program_output[0]
            message_string.rstrip()

            message_string = to_bytes(message_string)

            print(program_output_data.get("result", False))

            if program_output_data.get("result", False) == "TL":
                message_string = "<killed> ( timed out )"
            elif program_output_data.get("result", False) == "RF":
                message_string = \
                    "<killed> ( restricted function used: %d(%d) )" % (
                        program_output_data.get("syscall_info")[0],
                        program_output_data.get("syscall_info")[1]
                    )
            elif program_output_data.get("result", False) == "ML":
                message_string = "<killed> ( memory limit exceeded )"
            else:
                if program_output[0]:

                    if len(program_output) > 1:
                        message_string = to_bytes(
                            message_string +
                            " [+%d deleted lines]" % (len(program_output) - 1)
                        )

                    max_msg_len = 400 - len("[+nnn deleted bytes]")
                    if len(message_string) > max_msg_len:
                        message_string = (
                            message_string[:max_msg_len] +
                            (
                                "[+%d deleted bytes]" %
                                (len(message_string) - max_msg_len)
                            )
                        )

                else:
                    message_string = "<no output> ( return value was %d ) " % (
                        program_output_data.get("exitcode", -1)
                    )

            return message_string

    def snippet(self, data, extra_args):
        message = data["message"]

        if message.destination == self.connection.config.nick:
            dest = message.sender.nick
        else:
            dest = message.destination

        rand_name = random.randint(0, 1000)

        output_filename = ""
        code_filename = ""

        while 1:
            output_filename = "files/output/%d" % rand_name
            code_filename = "files/output/code.%d.%s" % (
                rand_name, extra_args.get("lang_extension", None)
            )
            if(
                not os.path.isfile(output_filename) and
                not os.path.isfile(code_filename)
            ):
                break

        code_file = open(code_filename, "w+")
        for prefix_file in extra_args.get("prefix_files", []):
            code_prefix_file = open(prefix_file, "r")
            code_file.write(code_prefix_file.read())
            code_prefix_file.close()
            code_file.write("\n")

        code_file.write(data["command"])

        for suffix_file in extra_args.get("suffix_files", []):
            code_suffix_file = open(suffix_file, "r")
            code_file.write(code_suffix_file.read())
            code_suffix_file.close()
            code_file.write("\n")
        code_file.flush()
        code_file.close()

        try:
            self.compile_code(code_filename, output_filename)
        except CompilerException as e:
            self.connection.send_message(irc.IRCPrivateMessage(dest, e.error))
        else:
            self.connection.send_message(
                irc.IRCPrivateMessage(dest, self.run(output_filename))
            )

        try:
            os.remove(output_filename)
            os.remove(code_filename)
        except Exception as e:
            print(e)

        return True

    def handle_call(self, message, **kwargs):
        self.connection = kwargs.get("connection", None)
        for command in self.commands:
            data = command.is_called(message, **kwargs)
            if not data:
                continue

            return command.function(data, command.extra_args)
        return False

    def __init__(self, **kwargs):
        self.connection = kwargs.get("connection", None)
        self.commands = []
        self.out_flag = "-o"
        self.run_cmd = None
