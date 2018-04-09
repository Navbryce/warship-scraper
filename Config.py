import json

def getConfigFromPath(filePath):
    """Used to get config dictionary from file path"""
    with open(filePath, 'r') as file: #If either passing only JSON or two file paths (See help message at bottoms), settings still need to be "read" in
        config = json.load(file)
    config["dbPort"] = int(config["dbPort"]) # has to be in the form of an int
    if len(config["mUser"]) == 0:
        config["mUser"] = None
    if len(config["mPass"]) == 0:
        config["mPass"] = None
    return config
