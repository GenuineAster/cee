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
import string
import time
import json
import subprocess
import re
from easyprocess import EasyProcess
from irc.irc import *
from plugins.BasePlugin import *
from pluginmanager.pluginmanager import *

plugin_manager = PluginManager()
plugin_manager.get_plugins()

IRC = IRCConnection(IRCConfig(host="irc.esper.net"))
IRC.start()
IRC.join_channel("#Ultros")

plugin_manager.load_plugins(connection=IRC)


while 1:
	IRC.parse_buffer()

	for message in IRC.get_messages():
		print("%s:\t<%s> %s" % (message.destination, message.sender.nick, message.message))

		for plugin in plugin_manager.plugins:
			if plugin.plugin_object.handle_call(message):
				break;


	time.sleep(0.001)