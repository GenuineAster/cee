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
from threading import Thread
from irc.irc import *
from plugins.BasePlugin import *
from pluginmanager.pluginmanager import *
from configloader.configloader import *

config_full = get_config("config/cee.conf")

def run_irc_instance(config):
	plugin_manager = PluginManager()
	plugin_manager.get_plugins()

	IRC = IRCConnection(IRCConfig(config=config))
	IRC.start()

	plugin_manager.load_plugins(connection=IRC)


	while 1:
		IRC.parse_buffer()

		for message in IRC.get_messages():
			print("%s:\t<%s> %s" % (message.destination, message.sender.nick, message.message))

			for plugin in plugin_manager.plugins:
				if plugin.plugin_object.handle_call(message):
					break;


		time.sleep(0.001)

threads = []


for network_name in config_full["IRC"]:
	irc_config = config_full["IRC"][network_name]
	print(irc_config["host"])
	threads.append(Thread(target=run_irc_instance, args=[irc_config]))
	threads[-1].start()
