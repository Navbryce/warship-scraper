import json
import sys
sys.path.insert(0, "../..")
from ABoatScraping.Calculate import Calculate
from ABoatScraping.ABoatDatabase import BoatDatabase
from Edge import Edge

class ShipCompare(object):
    def __init__ (self, shipOne, shipTwo):
        self.shipOne = shipOne
        self.shipTwo = shipTwo
        self.edge = Edge(self.shipOne["scrapeURL"], self.shipTwo["scrapeURL"], 0, [])

        self.runDateComparisons()


    def addEdge(self, source, target, magnitude, reasons):
        """
        adds to magnitude of existing edge
        """
        existingEdge = self.edge
        existingEdge.incrementMagnitude(magnitude, reasons)

    def getSerializableEdge(self):
        """ Returns the seraliazed edges between ships in array. Each object of the array is an Edge object"""
        return self.edge.toSerializableForm()

    def runDateComparisons(self):
        """runs the comparison tests involved with dates. only run date comparison tests for types of dates all ships have in order to keep the edges balanced"""
        datesToCheckFor = ['laid down', 'launched', 'commissioned']
        shipOneDates = self.shipOne["importantDates"]
        shipTwoDates = self.shipTwo["importantDates"]
        for dateToCheckFor in datesToCheckFor:
            shipOneHasDate = dateToCheckFor in shipOneDates
            shipTwoHasDate = dateToCheckFor in shipTwoDates

            if shipOneHasDate and shipTwoHasDate:
                if self.compareDate(shipOneDates[dateToCheckFor], shipTwoDates[dateToCheckFor]): # they are within tolerances
                    self.addEdge(self.shipOne["scrapeURL"], self.shipTwo["scrapeURL"], 1, ["Within tolerances of date for " + dateToCheckFor])
            else:
                if not shipOneHasDate:
                    print(self.shipOne["displayName"] + " does not have a date for " + dateToCheckFor)
                if not shipTwoHasDate:
                    print(self.shipTwo["displayName"] + " does not have a date for " + dateToCheckFor)

    #Compare functions
    def compareDate(self, date_one_object, date_two_obect):
        return Calculate.withinRange(date_one_object["year"], date_two_obect["year"], 5) # if they were made within a + 5 year, -5 year range

    def compareValue(self, value_one, value_two):
        """compares values within the standard tolerance. certain values might want a custom tolerance. this just provides a standard method"""
        return Calculate.withinTolerance(value_one, value_two, .05) #5% tolerance

# Test script 
boatDatabase = BoatDatabase("localhost", 27017)
filter = {"scrapeURL": "https://en.wikipedia.org/wiki/German_battleship_Scharnhorst"}
ship_one = boatDatabase.findShips(filter)[0]
filter = {"scrapeURL": "https://en.wikipedia.org/wiki/German_battleship_Gneisenau"}
ship_two = boatDatabase.findShips(filter)[0]
shipCompareTest = ShipCompare(ship_one, ship_two)
print(json.dumps(shipCompareTest.getSerializableEdge()))
