import socket
import time
import string
from kitchen.text.converters import to_bytes
from threading import Thread


class IRCChannel(object):
    """Simple channel data"""
    name = None
    joined = None
    active = None

    def __init__(self, name):
        self.name = name
        self.joined = False
        self.active = True


class IRCConfig(object):
    port = None
    host = None
    nick = None
    user = None
    ident = None
    realname = None
    channels = None

    def __init__(self, **kwargs):
        self.host = kwargs.get("host", "")
        self.port = kwargs.get("port", 6667)
        self.nick = kwargs.get("nick", "cee")
        self.user = kwargs.get("user", "cee")
        self.ident = kwargs.get("ident", "cee")
        self.realname = kwargs.get("realname", "cee, the C++ eval bot")
        self.channels = kwargs.get("channels", {})

        if kwargs.get("config", False):
            config = kwargs["config"]
            self.host = config.get("host", "").rstrip()
            self.port = config.get("port", 6667)
            self.nick = config.get("nick", "cee").rstrip()
            self.user = config.get("user", "cee").rstrip()
            self.ident = config.get("ident", "cee").rstrip()
            self.realname = config.get(
                "realname",
                "cee, the C++ eval bot"
            ).rstrip()
            channels = config.get("channels", [])
            for channel in channels:
                self.channels[channel] = IRCChannel(channel)


class IRCUser:
    user_string = None
    nick = None

    def __init__(self, raw):
        self.user_string = raw
        self.nick = raw.split("!")[0][1:]


class IRCPrivateMessage(object):
    sender = IRCUser("")
    destination = ""
    message = ""

    def parse_string(self, raw_message):
        parts = raw_message.split()
        if parts[1] != "PRIVMSG":
            return

        self.sender = IRCUser(parts[0])
        self.destination = parts[2]

        message = parts[3:]
        self.message = string.join(message, " ")
        self.message = self.message[1:]

    def __init__(self, *args):
        if len(args) == 1:
            self.parse_string(args[0])
        elif len(args) == 2:
            self.destination = args[0]
            self.message = args[1]
        elif len(args) == 3:
            self.sender = args[0]
            self.destination = args[1]
            self.message = args[2]


class IRCConnection(object):
    config = None
    sock = None
    readlines = None
    readbuffer = None
    channels = None
    messages = None
    ready = None
    socket_recieve_thread = None
    channel_thread = None

    def join_channel(self, channel):
        self.channels[channel] = IRCChannel(channel)

    def join_channels(self, channels):
        for channel in channels.split(","):
            self.join_channel(channel)

    def part_channel(self, channel):
        self.channels[channel].active = False

    def part_channels(self, channels):
        for channel in channels.split(","):
            self.part_channel(channel)

    def process_channels(self):
        while 1:
            time.sleep(0.5)
            if self.ready:
                for channel in self.channels:
                    if self.channels[channel].active:
                        if not self.channels[channel].joined:
                            self.socket_send("JOIN %s" % channel)
                    else:
                        if self.channels[channel].joined:
                            self.socket_send("PART %s" % channel)

    def parse_buffer(self):
        lines = self.readlines[:]

        for raw_line in lines:
            #print(raw_line)

            line = raw_line
            line = string.rstrip(line)
            line = string.split(line)

            try:

                if line[0] == "PING":
                    self.socket_send("PONG %s" % line[1])

                if line[1] == "001":
                    self.ready = True

                if self.ready:
                    if line[1] == "JOIN":
                        if IRCUser(line[0]).nick == self.config.nick:
                            self.channels[line[2].lstrip(":")].joined = True
                    if line[1] == "KICK":
                        if line[3] == self.config.nick:
                            self.channels[line[2]].joined = False
                    if line[1] == "PART":
                        if line[3] == self.config.nick:
                            self.channels[line[2]].joined = False
                    if line[1] == "PRIVMSG":
                        self.messages.append(IRCPrivateMessage(raw_line))
            except IndexError:
                print("Caught IndexError in parse_buffer")

            else:
                try:
                    self.readlines.pop(0)
                except IndexError:
                    pass

    def connect(self):
        if self.config.host == "":
            return
        self.sock.connect((self.config.host, self.config.port))

    def socket_read(self):
        while 1:
            try:
                self.readbuffer += self.sock.recv(1024)
            except socket.error:
                print("Socket isn't open. Nice try.")
            else:
                temp = string.split(self.readbuffer, "\n")
                for line in temp:
                    self.readlines.append(line)
                self.readbuffer = self.readlines.pop()
            time.sleep(0.1)

    def socket_send(self, data):
        try:
            self.sock.send("%s\r\n" % to_bytes(data))
        except socket.error:
            print("Socket isn't open. Nice try.")

    def start(self):
        self.connect()
        self.socket_send("NICK %s" % self.config.nick)
        self.socket_send("USER %s %s bla :%s" % (
            self.config.ident,
            self.config.host,
            self.config.realname
        ))

        socket_recieve_thread = Thread(target=self.socket_read)
        socket_recieve_thread.start()

        channel_thread = Thread(target=self.process_channels)
        channel_thread.start()

    def get_messages(self):
        messages = self.messages[:]
        self.messages = []
        return messages

    def send_message(self, message):
        self.socket_send("PRIVMSG %s :%s" % (
            message.destination,
            message.message
        ))

    def __init__(self, config):
        self.config = config
        self.channels = self.config.channels
        self.sock = socket.socket()
        self.readlines = []
        self.readbuffer = ""
        self.messages = []
        self.ready = False
