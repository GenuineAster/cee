#!/usr/bin/env python
# coding=utf-8

"""
cee - The C++-evaluating IRC bot (written in Python)

Please run this file.
Please?

Also, there's a README, and a LICENSE file.
I chose MIT as a license because it rocks.


Pull requests and stuff are welcome. Just don't break
 my beloved cee.

"""
import sys
import socket
import string
import time
from threading import Thread
from irc.irc import *

IRC = IRCConnection(IRCConfig(host="irc.esper.net"))
IRC.start()
IRC.join_channel("#Ultros")


while 1:
	IRC.parse_buffer()

	for message in IRC.get_messages():
		print("%s:\t<%s> %s" % (message.destination, message.sender.get_nick(), message.message))

	time.sleep(0.001)