import json
import sys
from ship_compare.ship_compare import ShipCompare
from ship_compare.Edge import Edge
sys.path.insert(0, "../..")
from ABoatScraping.Calculate import Calculate
from ABoatScraping.ABoatDatabase import BoatDatabase


class DatabaseCompare(object):
    def __init__ (self, ship):
        self.ship = ship
        self.edges = {} # A dictionary where each property is an edge + "+" + source combination
        self.database = BoatDatabase("localhost", 27017)
        queryFilter = {"scrapeURL": { # get all ships other than the ship
            "$ne": ship.scrapeURL
        }}
        otherShips = self.database.findShips(queryFilter)
        self.compareToArrayOfShips(otherShips)

    def compareToArrayOfShips(self, ships):
        for ship in ships:
            self.compareShips(ship)

    def compareShips(self, otherShip):
        comparison = ShipCompare(self.ship, otherShip)
        self.addEdge(comparison.edge)

    def addEdge(self, edge): # if the edge already exists (same target and source combination), it will increment the magnitude of the edge. else it will create the edge
        """
        reasons should an array of strings
        checks to see if edge already exists
        """
        key = self.generatePropertyKey(edge["source"], edge["target"])
        if key in self.edges: # the edge is already in the array
            existingEdge = self.edges[key]
            existingEdge.incrementMagnitude(edge["magnitude"], edge["reasons"])
        else:
            self.edges[key] = edge

    def generatePropertyKey(self, source, target):
        """generates a 'propertykey'. Essentially a key in the edges map (AKA python dictionary) """
        return source + "+" + target

    def getSerializableEdgesBetweenShips(self):
        """ Returns the seraliazed edges between ships in array. Each object of the array is an Edge object"""
        serializedEdges = []
        for edgeKey in self.edges:
            serializedEdges.append(self.edges[edgeKey].toSerializableForm())
        return serializedEdges
