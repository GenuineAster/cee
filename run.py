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

sys.dont_write_bytecode = True

import time
from threading import Thread
import irc
import pluginmanager
import configloader
import traceback


config_full = configloader.get_config("config/cee.conf")


def run_command(message, plugin_manager, IRC):
    for plugin in plugin_manager.plugins:
        try:
            if plugin.plugin_object.handle_call(
                message,
                plugin_manager=plugin_manager,
                connection=IRC
            ):
                break
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)


def run_irc_instance(config, plugin_manager):

    IRC = irc.IRCConnection(irc.IRCConfig(config=config))
    IRC.start()

    command_threads = []
    command_queue = []

    while 1:
        IRC.parse_buffer()

        for message in IRC.get_messages():
            print("%s:\t<%s> %s" % (
                message.destination,
                message.sender.nick,
                message.message
            ))

            command_queue.append(message)

        temp_command_queue = command_queue[:]

        for i, command in enumerate(temp_command_queue):
            if len(command_threads) < config_full.get("max_concurrent_commands", 1):  # noqa
                command_threads.append(
                    Thread(
                        target=run_command,
                        args=[
                            command, plugin_manager, IRC
                        ]
                    )
                )
                command_threads[-1].start()
                try:
                    if len(command_queue) > i:
                        command_queue.pop(i)
                except Exception as e:
                    print(e)

        for i, thread in enumerate(command_threads):
            if not thread.isAlive():
                command_threads.pop(i)

        time.sleep(0.01)

threads = []

plugin_manager = pluginmanager.PluginManager()
plugin_manager.get_plugins()
plugin_manager.load_plugins()

for network_name in config_full["IRC"]:
    irc_config = config_full["IRC"][network_name]
    threads.append(
        Thread(target=run_irc_instance, args=[irc_config, plugin_manager])
    )
    threads[-1].start()
