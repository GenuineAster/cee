import re
from kitchen.text.converters import to_bytes


class Command(object):
    prefixes = None
    words = None
    function = None
    extra_args = None

    def find_prefix(self, message, **kwargs):
        for prefix in self.prefixes:
            findstring = prefix[:]
            findstring = re.sub(
                "%%nick%%",
                kwargs.get("connection", None).config.nick,
                findstring
            )
            findstring = re.sub(
                "%%prefix%%",
                kwargs.get("command_prefix", ""),
                findstring
            )

            findstring = to_bytes(findstring)
            msg = to_bytes(message.message)
            if msg.startswith(findstring):
                return findstring
        return None

    def is_called(self, message, **kwargs):
        prefix = self.find_prefix(message, **kwargs)
        if not prefix:
            return False

        command = message.message[len(prefix):]

        command = command.lstrip()
        command = command.lstrip(":")
        command = command.lstrip(",")
        command = command.lstrip()

        for word in self.words:
            if command.startswith(word):
                return {
                    "prefix": prefix,
                    "word": word,
                    "command": command,
                    "connection": kwargs.get("connection", None),
                    "message": message
                }

        return False

    def __init__(self, func, prefixes, words, extra_args={}):
        self.function = func
        self.prefixes = prefixes
        self.words = words
        self.extra_args = extra_args


class BasePlugin(object):
    name = None
    author = None
    description = None
    commands = None

    connection = None

    def handle_call(self, message, **kwargs):
        raise NotImplementedError(
            "Please implement handle_call in plugin " % self.name
        )

    def __init__(self, **kwargs):
        self.connection = kwargs.get("connection", None)
