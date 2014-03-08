import json


def get_config(filename):
    try:
        fh = open(filename, "r")
        config = fh.read()
        return json.loads(config)
    except IOError:
        print("Oops! %s doesn't seem to exist." % filename)
        return None
