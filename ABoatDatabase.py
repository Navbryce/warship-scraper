from pymongo import MongoClient
from ABoatScraping.utilities.get_environment import CONFIG_PATH
from ABoatScraping import Config

class BoatDatabase(object):
    def __init__(self, ip, port, userName = None, password = None, databaseName = None):
        """
        ipString = "ip:port"
        """

        config = Config.getConfigFromPath(CONFIG_PATH)
        if databaseName is None:
            databaseName = config["databaseName"]
        self.ip = ip
        self.port = port
        self.client = MongoClient(ip, port)
        self.database = self.client[databaseName]
        if userName is None or password is None:
            userName = config["mUser"]
            password = config["mPass"]
            if userName is not None and password is not None:
                self.database.authenticate(userName, password)
            elif userName is not None or password is not None:
                print("Both a username and password must be configured in the config (mUser and mPass) or must be passed as a parameter or NOTHING at all")

        self.shipsCollection = self.database.ships

    def closeConnection(self):
        self.client.close()

    def deleteShips (self, filter):
        return self.shipsCollection.delete_many(filter)

    def findShips(self, filterDictionary):
        """
        Will return an array of ships dictionaries that match the filter.
        filterDictionary - See MongoDB "find filters" for more information on filters
        """
        return self.shipsCollection.find(filterDictionary)

    def insertSingleShip(self, ship):
        """
        ship - Must be a dictionary. ShipURL must be unique
        Returns objectID of inserted ship
        """
        return self.shipsCollection.insert(ship)

    def insertShips(self, ships):
        """
        ships - Array of ship dictionaries
        Returns ships' objectIDs in the database
        """
        return self.shipsCollection.insert(ships)

    def protectedInsertShip(self, ship):
        """
        ship - Must be a dictionary. ShipURL does not need to be unique. If not unique, the existing ship will be deleted and the new one will be inserted.
        Returns objectID of inserted ship
        """
        ship = ship.copy() #Copied because the insert method for the Mongo Package adds an "ObjectID" field to the ship that is not JSON serliazable (REMOVE in final version to optimize performance)
        filterDictionary = {"scrapeURL": ship["scrapeURL"]}
        existingShip = self.shipsCollection.find_one(filterDictionary)
        if existingShip is not None:
            self.shipsCollection.delete_one(filterDictionary) #Deletes the existing ship. There should only be one ship with a matching URL at MOST.
        return self.insertSingleShip(ship)

    def protectedInsertShips(self, ships):
        """
        ships - Must be an array of ships dictionaries. shipURLs do NOT need to be unique. If not unique, the existing ship will be deleted and the new one will be inserted.
        Returns objectIDs array of inserted ships
        """
        insertedObjectIds = []
        for ship in ships:
            insertedObjectIds.append(self.protectedInsertShip(ship))
        return insertedObjectIds

    def updateShip(self, ship):
        """Will update an existing document that has the same scrapeURL with the ship dictionary. If the document doesn't exist
        it will create the document"""
        self.shipsCollection.update_one({"scrapeURL": ship["scrapeURL"]}, {"$set": ship}, upsert=True)
