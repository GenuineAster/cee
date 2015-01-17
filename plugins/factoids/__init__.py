import time
import irc
import plugins.BasePlugin

class Factoid:
    name = None
    author_created = None
    author_edited = None
    date_created = None
    date_edited = None
    factoid = None

class Plugin(plugins.BasePlugin.BasePlugin, object):

    name = None
    author = None
    description = None
    connection = None
    factoids = None

    def factinfo(self, data):
        dest = ""
        message = data["message"]
        if message.destination == self.connection.config.nick:
            dest = message.sender.nick
        else:
            dest = message.destination

        cmd = data.get("command", "")
        cmd.lstrip().rstrip()
        factoid_name = cmd.split(" ", 1)[0]                                                             
        factoids_match = [x for x in self.factoids if x.name == factoid_name]
        if factoids_match:
            factoid = factoids_match[0]
        msg = irc.IRCPrivateMessage(
            dest,
            "%s: factoid %s created by %s at %s" % (message.sender.nick, factoid.name, factoid.author_created, time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(factoid.date_created)))
        )
        self.connection.send_message(msg)
        return True        

        
    def factoid(self, data):
        dest = ""                                                                                                   
        message = data["message"]                                                                                   

        if message.destination == self.connection.config.nick:                                                      
            dest = message.sender.nick                                                                              
        else:                                                                                                       
            dest = message.destination                                                                              
                                             
        cmd = data.get("full_command", "")
        cmd.lstrip().rstrip()
        factoid_name = cmd.split(" ", 1)[0]
        
        factoids_match = [x for x in self.factoids if x.name == factoid_name]
        if factoids_match:
            factoid_msg = factoids_match[0].factoid
            msg = irc.IRCPrivateMessage(                                                                                
                dest,                                                                                                   
                "%s: %s" % (message.sender.nick, factoid_msg)
            )
        else:
            msg = irc.IRCPrivateMessage(dest, "Factoid not found: %s" % factoid_name)

        self.connection.send_message(msg)                                                                           
        return True                                                                                                 


    def add(self, data):

        dest = ""
        message = data["message"]

        if message.destination == self.connection.config.nick:
            dest = message.sender.nick
        else:
            dest = message.destination

        fact = Factoid()
        fact.author_created = message.sender.nick
        fact.date_created = time.time()
        fact.author_edited = message.sender.nick
        fact.date_edited = time.time()
        cmd = data.get("command", "")
        cmd.lstrip()
        cmd.rstrip()
        fact.name = cmd.split(" ", 1)[0]
        fact.factoid = cmd.split(" ", 1)[1]

	m = False
	for p in data.get("plugin_manager", "").plugins:
            for c in p.plugin_object.commands:
                for pre in c.prefixes:
                    for x in [x for x in pre if (x.lstrip("%%nick%%") == fact.name) or (x.lstrip("%%prefix%%") == fact.name)]:
                        m = True
                for w in c.words:
                    if w == fact.name:
                        m = True
        if not m:
            self.factoids.append(fact)
            self.commands.append(
                plugins.BasePlugin.Command(self.factoid, ["%%nick%%", "%%prefix%%"], [fact.name])
            )

            msg = irc.IRCPrivateMessage(
                dest,
                "%s: factoid added: %s: %s." % (message.sender.nick, fact.name, fact.factoid)
            )
        else:
            msg = irc.IRCPrivateMessage(
                dest,
                "%s: factoid `%s` already exists or name is already in use." % (message.sender.nick, fact.name
            ))
        self.connection.send_message(msg)
        return True

    def handle_call(self, message, **kwargs):
        self.connection = kwargs.get("connection", None)
        for command in self.commands:
            data = command.is_called(message, **kwargs)
            if not data:
                continue
            data["plugin_manager"] = kwargs.get("plugin_manager", None)
            return command.function(data)
        return False

    def __init__(self, **kwargs):
        self.name = "factoids"
        self.author = "Mischa-Alff"
        self.description = "This plugin provides factiod support for cee."

        self.connection = kwargs.get("connection", None)

        self.commands = []

        self.commands.append(
            plugins.BasePlugin.Command(
                self.add, ["%%prefix%%", "%%name%%"], ["add", "factadd", "factoidadd"]
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.factinfo, ["%%prefix%%", "%%name%%"], ["factinfo", "fi", "facti"]
            )
        )
        self.commands.append(
            plugins.BasePlugin.Command(
                self.factoid, ["%%prefix%%", "%%name%%"], ["factoid", "fact"]
            )
        )

        self.factoids = []
