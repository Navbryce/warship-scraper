from Edge import Edge

class ShipCompare(object):
    def __init__ (self, shipOne, shipTwo):
        self.shipOne = shipOne
        self.shipTwo = shipTwo
        self.edges = {} # A dictionary where each property is an edge + "+" + source combination


    def addLink (self, source, target, magnitude, reasons):
        """
        reasons should an array of strings
        checks to see if edge already exists
        """
        key = self.generatePropertyKey(source, target)
        if key in self.edges: # the edge is already in the array
            existingEdge = self.edges[key]
            existingEdge.incrementMagnitude(magnitude, reasons)

    def createEdge (self, source, target, magnitude, reasons):
        """
        creates edges
        does not check to see if edge exists, so if the same edge already exists, the new edge will overrite it
        """
        edge = Edge(source, target, magnitude, reasons)
        self.edges[self.generatePropertyKey(source, target)] = edge

    def generatePropertyKey (self, source, target):
        """generates a 'propertykey'. Essentially a key in the edges map (AKA python dictionary) """
        return source + "+" + target;

    def getEdgesBetweenShips(self):
        """ Returns the edges between ships in array. Each object of the array is an Edge object"""
        return self.edges
