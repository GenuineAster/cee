import os
import sys
import re
from kitchen.text.converters import to_bytes
import easyprocess
import irc
import plugins.BasePlugin
import utils.Compile
import sandbox

compiler_golf = [
    "clang++",
    "-std=c++11",
    "-w",
    "-fmessage-length=0",
    "-ftemplate-depth-128",
    "-fno-elide-constructors",
    "-fstack-protector-all"
]


system, machine = os.uname()[0], os.uname()[4]


class MiniSandbox(sandbox.SandboxPolicy, sandbox.Sandbox):
    sc_table = None
    # white list of essential linux syscalls for statically-linked C programs
    sc_safe = dict(
        i686=set(
            [
                0, 3, 4, 19, 45, 54, 90, 91, 122, 125, 140, 163, 192, 197,
                224, 243, 252
            ]
        ),
        x86_64=set(
            [
                0,   1,   2,   3,   4,   5,   6,   7,   8,   9,   10,  11,   # noqa
                12,  13,  14,  15,  16,  17,  18,  19,  20,  21,  22,  23,   # noqa
                24,  25,  26,  27,  28,  29,  30,  31,  32,  33,  34,  35,   # noqa
                36,  37,  38,  39,  40,  41,  42,  43,  44,  45,  46,  47,   # noqa
                48,  49,  50,  51,  52,  53,  54,  55,  60,  61,  62,  63,   # noqa
                64,  65,  66,  67,  68,  69,  70,  71,  72,  73,  74,  75,   # noqa
                76,  77,  78,  79,  80,  81,  82,  83,  84,  85,  86,  87,   # noqa
                88,  89,  90,  91,  92,  93,  94,  95,  96,  97,  98,  99,   # noqa
                100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,  # noqa
                112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123,  # noqa
                124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135,  # noqa
                136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147,  # noqa
                148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,  # noqa
                160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171,  # noqa
                172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183,  # noqa
                184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195,  # noqa
                196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207,  # noqa
                208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219,  # noqa
                220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231,  # noqa
                232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243,  # noqa
                244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255,  # noqa
                256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267,  # noqa
                268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279,  # noqa
                280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291,  # noqa
                292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303,  # noqa
                304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315,  # noqa
                316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327,  # noqa
                328, 329, 330
            ]
        ),
    )
    # result code translation table
    result_name = dict(
        (
            getattr(sandbox.Sandbox, 'S_RESULT_%s' % r), r
        )
        for r in (
            'PD', 'OK', 'RF', 'RT', 'TL', 'ML', 'OL', 'AT', 'IE', 'BP'
        )
    )

    def __init__(self, *args, **kwds):
        # initialize table of system call rules
        self.sc_table = dict()
        if machine == 'x86_64':
            for (mode, abi) in ((0, 'x86_64'), (1, 'i686'), ):
                for scno in MiniSandbox.sc_safe[abi]:
                    self.sc_table[(scno, mode)] = self._CONT
        else:  # i686
            for scno in MiniSandbox.sc_safe[machine]:
                self.sc_table[scno] = self._CONT
        # initialize as a polymorphic sandbox-and-policy object
        sandbox.SandboxPolicy.__init__(self)
        sandbox.Sandbox.__init__(self, *args, **kwds)
        self.policy = self  # apply local policy rules

    def probe(self):
        # add custom entries into the probe dict
        d = sandbox.Sandbox.probe(self, False)
        d['cpu'] = d['cpu_info'][0]
        d['mem'] = d['mem_info'][1]
        d['result'] = MiniSandbox.result_name.get(self.result, 'NA')
        return d

    def __call__(self, e, a):
        # handle SYSCALL/SYSRET events with local rules
        if e.type in (sandbox.S_EVENT_SYSCALL, sandbox.S_EVENT_SYSRET):
            scinfo = (e.data, e.ext0) if machine == 'x86_64' else e.data
            rule = self.sc_table.get(scinfo, self._KILL_RF)
            #print({sc_table})
            return rule(e, a)
        # bypass other events to base class
        return sandbox.SandboxPolicy.__call__(self, e, a)

    def _CONT(self, e, a):  # continue
        a.type = sandbox.S_ACTION_CONT
        return a

    def _KILL_RF(self, e, a):  # restricted func.
        a.type, a.data = sandbox.S_ACTION_KILL, sandbox.S_RESULT_RF
        return a


class Plugin(plugins.BasePlugin.BasePlugin, object):

    name = None
    author = None
    description = None
    connection = None

    def compile_code(self, filename, output):
        compiler_output_raw = ""
        compiler_output = []
        compiler_command_temp = compiler_golf[:]
        compiler_command_temp.append(filename)
        compiler_command_temp.append("-o%s" % output)
        compiler_process_data = easyprocess.EasyProcess(
            compiler_command_temp
        ).call(timeout=30)
        compiler_output_raw = (
            compiler_process_data.stdout + compiler_process_data.stderr
        )

        if compiler_output_raw:
            compiler_output = compiler_output_raw.split("\n")
            compiler_output = filter(
                lambda x: re.search(r"(error|warning):", x),
                compiler_output
            )
            for i in range(len(compiler_output)):
                compiler_output[i] = compiler_output[i].split(" ", 1)[1]

            raise utils.Compile.CompilerException(compiler_output[0])

            return False

        else:
            return True

    def run(self, filename):
        program_output_raw = ""
        message_string = ""

        output = open("files/output/cee_output", "w+")

        cookbook = {
            'args': os.path.join(os.getcwd(), filename),
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
            msb = MiniSandbox(**cookbook)
            msb.run()
        except ValueError:
            return "<killed> ( recieved fork attempt )"
            output.flush()
            output.close()
        else:
            # verbose statistics
            program_output_data = msb.probe()

            output.flush()
            output.close()
            output = open("files/output/cee_output", "r")

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
            else:
                if program_output[0]:

                    if len(program_output) > 1:
                        message_string = to_bytes(
                            message_string +
                            " [+%d deleted lines]" % (len(program_output) - 1)
                        )

                    max_msg_len = 400 - len(" [+nnn deleted bytes]")
                    if len(message_string) > max_msg_len:
                        message_string = (
                            message_string[:max_msg_len] +
                            " [+%d deleted bytes]" % (
                                len(message_string) - max_msg_len
                            )
                        )

                else:
                    message_string = "<no output> ( return value was %d ) " % (
                        program_output_data.get("exitcode", -1)
                    )

            return message_string

    def snippet(self, data):
        message = data["message"]

        if message.destination == self.connection.config.nick:
            dest = message.sender.nick
        else:
            dest = message.destination

        try:
            os.remove("files/output/code.cpp")
            os.remove("files/output/output")
        except OSError as e:
            pass

        cpp_template_file = open("files/template.cpp", "r")
        cpp_file = open("files/output/code.cpp", "w+")
        cpp_file.write(cpp_template_file.read())
        cpp_template_file.close()
        cpp_file.write("\n")
        cpp_golf_file = open("files/golf.hpp", "r")
        cpp_file.write(cpp_golf_file.read())
        cpp_file.write("\n")
        cpp_golf_file.close()
        cpp_file.write(data["command"])
        cpp_file.flush()
        cpp_file.close()

        try:
            self.compile_code("files/output/code.cpp", "files/output/output")
        except utils.Compile.CompilerException as e:
            self.connection.send_message(
                irc.IRCPrivateMessage(dest, e.error)
            )
        else:
            self.connection.send_message(
                irc.IRCPrivateMessage(dest, self.run("files/output/output"))
            )

        return True

    def curly_brace_snippet(self, data):

        data["command"] = "int main()\n" + data["command"]
        return self.snippet(data)

    def stream_snippet(self, data):
        data["command"] = "{ cout " + data["command"] + "; }"
        return self.curly_brace_snippet(data)

    def handle_call(self, message, **kwargs):
        self.connection = kwargs.get("connection", None)
        for command in self.commands:
            data = command.is_called(message, self.connection)
            if not data:
                continue

            return command.function(data)
        return False

    def __init__(self, **kwargs):
        self.name = "golf"
        self.author = "Mischa-Alff"
        self.description = "A C++ golf plugin using clang++."

        self.connection = kwargs.get("connection", None)

        self.commands = []

        self.commands.append(
            plugins.BasePlugin.Command(
                self.curly_brace_snippet, ["golf"], ["{"]
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.stream_snippet, ["golf"], ["<<"]
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.snippet, ["golf"], [""]
            )
        )
