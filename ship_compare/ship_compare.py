import json
import sys
sys.path.insert(0, "A:\DevenirProjectsA")
from ABoatScraping.Calculate import Calculate
from ABoatScraping.ABoatDatabase import BoatDatabase
from ABoatScraping.ship_compare.Edge import Edge

class ShipCompare(object):
    tolerance = .05
    def __init__ (self, shipOne, shipTwo):

        self.shipOne = shipOne
        self.shipTwo = shipTwo
        self.edge = Edge(self.shipOne["scrapeURL"], self.shipTwo["scrapeURL"], 0, [])

        # Run comparisons
        self.runDateComparisons()
        self.runTypeAndClassComparisons()
        self.runComplementAndPhysicalComparison()
        self.runArmamentComparisons()
        self.runArmorComparisons()


    def addEdge(self, magnitude, reasons):
        """
        adds to magnitude of existing edge
        """
        existingEdge = self.edge
        existingEdge.incrementMagnitude(magnitude, reasons)

    def getSerializableEdge(self):
        """ Returns the seraliazed edges between ships in array. Each object of the array is an Edge object"""
        return self.edge.toSerializableForm()

    def runComplementAndPhysicalComparison(self):
        if self.doShipsHaveKey(["complement"]):
            if self.compareValue(self.shipOne["complement"], self.shipTwo["complement"]):
                self.addEdge(1, ["The ships are within tolerance, %s, for complement"%(self.tolerance)])
        for property, attributeDic in self.shipOne["physicalAttributes"].items():
            key = ["physicalAttributes"]
            if self.doShipsHaveKey(["physicalAttributes", property]):
                shipOneAttrib = self.shipOne["physicalAttributes"][property]
                shipTwoAttrib = self.shipTwo["physicalAttributes"][property]
                try:
                    if self.compareValue(shipOneAttrib["value"], shipTwoAttrib["value"], shipOneAttrib["unit"], shipTwoAttrib["unit"]):
                        self.addEdge(1, ["The ships are within tolerance, %s, for %s"%(self.tolerance, property)])
                except Exception as exception:
                    print(self.shipOne["displayName"] + ": ", shipOneAttrib)
                    print(self.shipTwo["displayName"] + ": ", shipTwoAttrib)


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
                    self.addEdge(1, ["Within tolerances of date for " + dateToCheckFor])
            else:
                if not shipOneHasDate:
                    print(self.shipOne["displayName"] + " does not have a date for " + dateToCheckFor)
                if not shipTwoHasDate:
                    print(self.shipTwo["displayName"] + " does not have a date for " + dateToCheckFor)

    def runTypeAndClassComparisons(self):
        """compares type and class"""
        if self.doShipsHaveKey(["type"]):
            if self.shipOne["type"] == self.shipTwo["type"]:
                self.addEdge(1, ["Ships are both of type, " + self.shipOne["type"]])
        if self.doShipsHaveKey(["class"]):
            if self.shipOne["class"] == self.shipTwo["class"]:
                self.addEdge(1, ["Boths ships are of the same class, " + self.shipOne["class"]])

    def runArmamentComparisons(self):
        """
        compare armaments
        in the future: have it compare individual weapons
        """
        for keyType, armamentType in self.shipOne["armament"].items():
            shipOneCalculate = armamentType["sizeCalculate"]
            shipTwoCalculate = self.shipTwo["armament"][keyType]["sizeCalculate"]
            if shipOneCalculate["noValues"] and shipTwoCalculate["noValues"]:
                # do nothing currently
                nothing = None
            else:
                if shipOneCalculate["noValues"] == shipTwoCalculate["noValues"]: # Both ships need to have values. not just one
                    # Don't give any weight (magnitude) to noValues if the ship have values
                    shipOneCalculate.pop("noValues")
                    shipTwoCalculate.pop("noValues")
                    self.compareDictionaries(shipOneCalculate, shipTwoCalculate, 1, keyType)
                    # Readd noValues in case the sames instances of these ships are used to be compared to new ships, the noValues key must exist initially
                    shipOneCalculate["noValues"] = False
                    shipTwoCalculate["noValues"] = False

    def runArmorComparisons(self):
        """runs comparisons for armor"""
        armorOne = self.shipOne["armor"]
        armorTwo = self.shipTwo["armor"]
        # if statement makes sure both ships have calculations for armor and the calculations actually have values
        if self.doDictionariesHaveKey(armorOne, armorTwo, ["calculations"]) and not armorOne["calculations"]["noValues"] and not armorTwo["calculations"]["noValues"]:
            armorOneCalc = armorOne["calculations"]
            print(armorOneCalc)
            armorTwoCalc = armorTwo["calculations"]
            print(armorTwoCalc)
            # don't give any weight to having False for novalues, so remove it from the dictionaries that will be compared
            armorOneCalc.pop("noValues")
            armorTwoCalc.pop("noValues")
            self.compareDictionaries(armorOneCalc, armorTwoCalc, 1, "armor")
            armorOneCalc["noValues"] = False
            armorTwoCalc["noValues"] = False

    # Compare functions
    def compareDate(self, date_one_object, date_two_obect):
        """used to compare dates"""
        return Calculate.withinRange(date_one_object["year"], date_two_obect["year"], 5) # if they were made within a + 5 year, -5 year range

    def compareValue(self, value_one, value_two, unitOne=None, unitTwo=None):
        """compares values within the standard tolerance. certain values might want a custom tolerance. this just provides a standard method"""
        if unitOne == unitTwo:
            return Calculate.withinTolerance(value_one, value_two, self.tolerance) #5% tolerance
        else:
            print("The two values don't have the same unit")
            return False
    def compareDictionaries(self, dictionaryOne, dictionaryTwo, magnitude, contextPhrase=""):
        """
        Assumes the dictionaries have the same keys and each key is associated with the same type
        magnitude - the magnitude that each key value has if they're equal
        """
        for key, value in dictionaryOne.items():
            if type(value) is dict:
                numberOfKeysInSubDict = len(value.items())
                self.compareDictionaries(value, dictionaryTwo[key], magnitude/numberOfKeysInSubDict, contextPhrase)
            else:
                if self.compareValue(value, dictionaryTwo[key]):
                    self.addEdge(magnitude, ["Boths ships are within the tolerance of %s for %s in %s"%(self.tolerance, key, contextPhrase)])
    # Other functions
    def doShipsHaveKey (self, keyArray):
        """checks to see if both ships have key. if both do, returns true"""
        return self.doDictionariesHaveKey(self.shipOne, self.shipTwo, keyArray)

    def doDictionariesHaveKey (self, object1, object2, keyArray):
        """checks to see if both objects have key. if both do, returns true"""
        if len(keyArray) == 0:
            return True
        else:
            key = keyArray[0]
            del keyArray[0]
            hasKey = True
            if key not in object1:
                hasKey = False
                print ("The property," + key + ",  is not in " + self.shipOne["displayName"])
            if key not in object2:
                hasKey = False
                print ("The property, " + key + ", is not in " + self.shipTwo["displayName"])
            if hasKey is False:
                return hasKey
            else:
                return self.doDictionariesHaveKey(object1[key], object2[key], keyArray)

# Test script
"""boatDatabase = BoatDatabase("localhost", 27017)
filter = {"scrapeURL": "https://en.wikipedia.org/wiki/German_battleship_Scharnhorst"}
ship_one = boatDatabase.findShips(filter)[0]
filter = {"scrapeURL": "https://en.wikipedia.org/wiki/German_battleship_Gneisenau"}
ship_two = boatDatabase.findShips(filter)[0]
shipCompareTest = ShipCompare(ship_one, ship_two)
print(json.dumps(shipCompareTest.getSerializableEdge()))
"""
