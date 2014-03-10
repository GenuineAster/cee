import re
from kitchen.text.converters import to_bytes


class Command(object):
    prefixes = None
    words = None
    function = None

    def find_prefix(self, message, connection):
        for prefix in self.prefixes:
            findstring = re.sub("%%nick%%", connection.config.nick, prefix)
            findstring = to_bytes(findstring)
            msg = to_bytes(message.message)
            if msg.startswith(findstring):
                return findstring
        return None

    def is_called(self, message, connection):
        prefix = self.find_prefix(message, connection)
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
                    "connection": connection,
                    "message": message
                }

        return False

    def __init__(self, func, prefixes, words):
        self.function = func
        self.prefixes = prefixes
        self.words = words


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
