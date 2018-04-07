from pymongo import MongoClient
from ABoatScraping.utilities.get_environment import CONFIG_PATH
from ABoatScraping import Config

class EdgeDatabase(object):
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

        self.edgesCollection = self.database.edges

    def closeConnection(self):
        self.client.close()

    def deleteEdges(self, filter):
        return self.edgesCollection.delete_many(filter)

    def getNeighbors(self, scrapeURL):
        """returns an array of neighbor dictionaries that are neighbors to the scrapeURL node. a neighbor dictionary contains a magnitude and scrapeURL"""
        filter = {
            "$or": [
                {
                    "target": scrapeURL
                },
                {
                    "source": scrapeURL
                }
            ]
        }
        edges = self.findEdges(filter)

        neighbors = []
        for edge in edges:
            if edge["source"] != scrapeURL:
                neighborURL = edge["source"]
            else:
                neighborURL = edge["target"]
            neighbor = {
                "scrapeURL": neighborURL,
                "magnitude": edge["magnitude"]
            }
            neighbors.append(neighbor)
        return neighbors

    def insertSingleEdge(self, edge):
        """
        edge - Must be a dictionary. edgeID (edge source and target) combination must be unique
        Returns objectID of inserted edge
        """
        return self.edgesCollection.insert(edge)

    def insertEdges(self, edges):
        """
        edges - Array of edge dictionaries with unique edge id's
        Returns edges' objectIDs in the database
        """
        return self.edgesCollection.insert(edges)

    def protectedInsertEdge(self, edge):
        """
        edge - Must be a dictionary. edge id does not need to be unique. If not unique, the existing edge will be deleted and the new one will be inserted.
        edge must also have a magnitude greater than 0
        Returns objectID of inserted edge
        """
        edge = edge.copy() #Copied because the insert method for the Mongo Package adds an "ObjectID" field to the edge that is not JSON serliazable (REMOVE in final version to optimize performance)
        filterDictionary = {"edgeId": edge["edgeId"]}
        existingEdge = self.edgesCollection.find_one(filterDictionary)
        if existingEdge is not None:
            self.edgesCollection.delete_one(filterDictionary) #Deletes the existing edge. There should only be one edge with a matching edgeId at MOST.
        if edge["magnitude"] > 0:
            self.insertSingleEdge(edge)

    def protectedInsertEdges(self, edges):
        """
        edges - Must be an array of edge dictionaries. edge id's do NOT need to be unique. If not unique, the existing edge will be deleted and the new one will be inserted.
        Returns objectIDs array of inserted edges
        """
        insertedObjectIds = []
        for edge in edges:
            insertedObjectIds.append(self.protectedInsertEdge(edge))
        return insertedObjectIds

    def findEdges(self, filterDictionary):
        """
        Will return an array of edge dictionaries that match the filter.
        filterDictionary - See MongoDB "find filters" for more information on filters
        """
        return self.edgesCollection.find(filterDictionary)
