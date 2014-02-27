import sys
import socket
import time
import string
from threading import Thread



class IRCChannel:
	"""Simple channel data"""
	name = ""
	joined = False
	active = True

	def __init__(self, name):
		self.name = name
		self.joined = False
		self.active = True



class IRCConfig:
	port = 6667
	host = ""
	nick = "cee"
	user = "cee"
	ident = "cee"
	realname = "cee, the C++ eval bot"
	channels = {}

	def __init__(self, **kwargs):
		for arg in kwargs:
			if arg == "host":
				self.host = kwargs[arg]
			elif arg == "port":
				self.port = kwargs[arg]
			elif arg == "nick":
				self.nick = kwargs[arg]
			elif arg == "user":
				self.user = kwargs[arg]
			elif arg == "ident":
				self.ident = kwargs[arg]
			elif arg == "realname":
				self.realname = kwargs[arg]
			elif arg == "channels":
				self.channels = kwargs[arg]


class IRCUser:
	user_string = ""

	def get_nick(self):
		return string.lstrip(self.user_string.split("!")[0], ":")

	def __init__(self, raw):
		self.user_string = raw

class IRCPrivateMessage:
	sender = IRCUser("")
	destination = ""
	message = ""

	def parse_string(self, raw_message):
		parts = raw_message.split()
		if parts[1] != "PRIVMSG":
			return

		self.sender.user_string = parts[0]
		self.destination = parts[2]

		message = parts[3:]
		self.message = string.join(message, " ")
		self.message = self.message[1:]

	def __init__(self, *args):
		if len(args) == 1:
			self.parse_string(args[0])
		elif len(args) == 3:
			self.sender = args[0]
			self.destination = args[1]
			self.message = args[2]


class IRCConnection:
	config = IRCConfig()
	sock = socket.socket()
	readlines = []
	readbuffer = ""
	channels = {}
	messages = []
	ready = False
	socket_recieve_thread = Thread()
	channel_thread = Thread()

	def join_channel(self, channel):
		self.channels[channel] = IRCChannel(channel)

	def part_channel(self, channel):
		self.channel[channel].active = False

	def process_channels(self):
		while 1:
			time.sleep(5)
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

			if len(line) < 1:
				continue;

			if line[0] == "PING":
				self.socket_send("PONG %s" % line[1])

			if line[1] == "001":
				self.ready = True

			if self.ready:
				if line[1] == "JOIN":
					if IRCUser(line[0]).get_nick() == self.config.nick:
						self.channels[line[2]].joined = True
				if line[1] == "KICK":
					if line[3] == self.config.nick:
						self.channels[line[2]].joined = False
				if line[1] == "PART":
					if line[3] == self.config.nick:
						self.channels[line[2]].joined = False
				if line[1] == "PRIVMSG":
					self.messages.append(IRCPrivateMessage(raw_line))

			self.readlines.pop(0)



	def connect(self):
		if self.config.host == "":
			return
		self.sock.connect((self.config.host, self.config.port))

	def socket_read(self):
		while 1:
			try:
				self.readbuffer+=self.sock.recv(1024)
			except socket.error as e:
				print("Socket isn't open. Nice try.")
			else:
				temp = string.split(self.readbuffer, "\n")
				for line in temp:
					self.readlines.append(line)
				self.readbuffer=self.readlines.pop()
			time.sleep(0.1)

	def socket_send(self, data):
		try:
			self.sock.send("%s\r\n" % data)
		except socket.error as e:
			print("Socket isn't open. Nice try.")

	def start(self):
		self.connect()
		self.socket_send("NICK %s" % self.config.nick)
		self.socket_send("USER %s %s bla :%s" % (self.config.ident, self.config.host, self.config.realname))

		socket_recieve_thread = Thread(target=self.socket_read)
		socket_recieve_thread.start()

		channel_thread = Thread(target=self.process_channels)
		channel_thread.start()

	def get_messages(self):
		messages = self.messages[:]
		self.messages = []
		return messages


	def __init__(self, config):
		self.config = config
		self.channels = self.config.channels
