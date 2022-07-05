import json
import os


def getConfigFromPath(filePath):
    """Used to get config dictionary from file path"""
    with open(filePath, 'r') as file: #If either passing only JSON or two file paths (See help message at bottoms), settings still need to be "read" in
        config = json.load(file)
    config["mongo_uri"] = os.environ["MONGO_URI"]
    config["dbName"] = os.environ["MONGO_DB_NAME"]
    return config
