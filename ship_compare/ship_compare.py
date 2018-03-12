import sys
sys.path.insert(0, "../..")
from ABoatScraping.Calculate import Calculate
from ABoatScraping.ABoatDatabase import BoatDatabase
from Edge import Edge

class ShipCompare(object):
    def __init__ (self, shipOne, shipTwo):
        self.shipOne = shipOne
        self.shipTwo = shipTwo
        self.edges = {} # A dictionary where each property is an edge + "+" + source combination


    def addLink(self, source, target, magnitude, reasons):
        """
        reasons should an array of strings
        checks to see if edge already exists
        """
        key = self.generatePropertyKey(source, target)
        if key in self.edges: # the edge is already in the array
            existingEdge = self.edges[key]
            existingEdge.incrementMagnitude(magnitude, reasons)

    def createEdge(self, source, target, magnitude, reasons):
        """
        creates edges
        does not check to see if edge exists, so if the same edge already exists, the new edge will overrite it
        """
        edge = Edge(source, target, magnitude, reasons)
        self.edges[self.generatePropertyKey(source, target)] = edge

    def generatePropertyKey(self, source, target):
        """generates a 'propertykey'. Essentially a key in the edges map (AKA python dictionary) """
        return source + "+" + target

    def getEdgesBetweenShips(self):
        """ Returns the edges between ships in array. Each object of the array is an Edge object"""
        return self.edges

    #Compare functions
    def compareDate(self, date_one_object, date_two_obect):
        return Calculate.withinRange(date_one_object.date.year, date_two_obect.date.year, 5) # if they were made within a + 5 year, -5 year range

    def compareValue(self, value_one, value_two):
        """compares values within the standard tolerance. certain values might want a custom tolerance. this just provides a standard method"""
        return Calculate.withinTolerance(value_one, value_two, .05) #5% tolerance

boatDatabase = BoatDatabase("localhost", 27017)
filter = {"scrapeURL": "https://en.wikipedia.org/wiki/German_battleship_Scharnhorst"}
ship_one = boatDatabase.findShips(filter)[0]
filter = {"scrapeURL": "https://en.wikipedia.org/wiki/German_battleship_Gneisenau"}
ship_two = boatDatabase.findShips(filter)[0]
shipCompareTest = ShipCompare(ship_one, ship_two)
print(shipCompareTest.edges)
