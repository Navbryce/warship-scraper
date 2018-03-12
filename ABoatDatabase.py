from pymongo import MongoClient

class BoatDatabase(object):
    def __init__(self, ip, port):
        """
        ipString = "ip:port"
        """
        self.ip = ip
        self.port = port
        self.client = MongoClient(ip, port)
        self.database = self.client.ABoat
        self.shipsCollection = self.database.ships

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

    def findShips(self, filterDictionary):
        """
        Will return an array of ships dictionaries that match the filter.
        filterDictionary - See MongoDB "find filters" for more information on filters
        """
        return self.shipsCollection.find(filterDictionary)
