import json
import os
import sys
ship_scraping_path = os.environ.get('SHIP_SCRAPER') # check environment variable. if not set, use a default value
if ship_scraping_path is None:
    ship_scraping_path = "A:\DevenirProjects"
else:
    ship_scraping_path += '/..'
sys.path.insert(0, ship_scraping_path)
from ABoatScraping.ABoatDatabase import BoatDatabase
from ABoatScraping.ship_compare.edge_database import EdgeDatabase
from ABoatScraping.ship_compare.ship_compare import ShipCompare
from ABoatScraping.utilities.get_environment import CONFIG_PATH
from ABoatScraping import Config

class DatabaseCompare(object):
    def __init__ (self, ship):
        configDictionary = Config.getConfigFromPath(CONFIG_PATH)
        databaseIP = configDictionary["dbIp"]
        databasePort = configDictionary["dbPort"]
        # print("Using %s:%s"%(databaseIP, databasePort))
        self.ship = ship
        self.edges = {} # A dictionary where each property is an edge + "+" + source combination
        self.boatDatabase = BoatDatabase(databaseIP, databasePort)
        self.edgeDatabase = EdgeDatabase(databaseIP, databasePort)
        queryFilter = {"scrapeURL": { # get all ships other than the ship
            "$ne": ship["scrapeURL"]
        }}
        otherShips = self.boatDatabase.findShips(queryFilter)
        self.compareToArrayOfShips(otherShips)

    def addEdge(self, edge): # if the edge already exists (same target and source combination), it will increment the magnitude of the edge. else it will create the edge
        """
        reasons should an array of strings
        checks to see if edge already exists
        """
        if edge.id in self.edges: # the edge is already in the array
            existingEdge = self.edges[edge.id]
            existingEdge.incrementMagnitude(edge.magnitude, edge.reasons)
        else:
            self.edges[edge.id] = edge

    def closeDatabases (self):
        self.boatDatabase.closeConnection()
        self.edgeDatabase.closeConnection()

    def compareToArrayOfShips(self, ships):
        for ship in ships:
            self.compareShips(ship)

    def compareShips(self, otherShip):
        comparison = ShipCompare(self.ship, otherShip)
        self.addEdge(comparison.edge)


    def getSerializableEdgesBetweenShips(self):
        """ Returns the seraliazed edges between ships in array. Each object of the array is an Edge object"""
        serializedEdges = []
        for edgeKey in self.edges:
            serializedEdges.append(self.edges[edgeKey].toSerializableForm())
        return serializedEdges
    def writeEdgesToDatabase(self):
        """
        will write edges to database. will override edge if it already exists
        """
        serializableEdges = self.getSerializableEdgesBetweenShips()
        self.edgeDatabase.protectedInsertEdges(serializableEdges)
"""
# Test script
boatDatabase = BoatDatabase("localhost", 27017)
filter = {"scrapeURL": "https://en.wikipedia.org/wiki/German_battleship_Scharnhorst"}
ship_one = boatDatabase.findShips(filter)[0]
databaseCompare = DatabaseCompare(ship_one)
databaseCompare.writeEdgesToDatabase() # writes the edges to database
print(json.dumps(databaseCompare.getSerializableEdgesBetweenShips()))
"""
