from pymongo import MongoClient

class EdgeDatabase(object):
    def __init__(self, ip, port):
        """
        ipString = "ip:port"
        """
        self.ip = ip
        self.port = port
        self.client = MongoClient(ip, port)
        self.database = self.client.ABoat
        self.edgesCollection = self.database.edges

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
        Returns objectID of inserted edge
        """
        edge = edge.copy() #Copied because the insert method for the Mongo Package adds an "ObjectID" field to the edge that is not JSON serliazable (REMOVE in final version to optimize performance)
        filterDictionary = {"edgeId": edge["edgeId"]}
        existingEdge = self.edgesCollection.find_one(filterDictionary)
        if existingEdge is not None:
            self.edgesCollection.delete_one(filterDictionary) #Deletes the existing edge. There should only be one edge with a matching edgeId at MOST.
        return self.insertSingleEdge(edge)

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