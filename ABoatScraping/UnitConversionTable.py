

class UnitConversionTable(object):
    ""
    conversionDictionary = {};


    def __init__(self):
        #First Key: "What you are converting from". Second Key: "What you are converting to". #mm is the primary unit we want to use, so everything will be able to convert to (and from it)
        self.conversionDictionary = {
            'mm': { # I honestly should have done this all the other way around where the primary key is what you're converting to.
                'cm': .1,
                'foot': 0.00328084,
                'ft': 0.00328084,
                'in': .0393701,
                'm': .001,
                'km': .000001,
                'mi': .000000621371,
                'nmi': .000000539956
            },
            'kn': {
                'knot': 1,
                'knots': 1,
                'mi/h': 1.15078,
                'km/h': 1.852
            },
            't': {
                'tons': 1
            },
            'word': {
                'single': 1,
                'double': 2,
                'dual': 2,
                'triple': 3,
                'quad': 4
            }
        }

    def convertUnit(self, value, currentUnit, newUnit):
        """Returns float'
           Recursive -- should never call itself more than once (AKA depth shouldn't exceed 2)
        """
        try:
            value = float(value)
        except (Exception):
            print("ERROR: An error occurred while trying to convert the value %s from %s to %s"%(value, currentUnit, newUnit))
        newValue = None
        if currentUnit == newUnit:
            newValue = value
        else:
            if currentUnit in self.conversionDictionary: #we can convert directly because currentUnit is a primary unit
                conversionConstantsArray = self.conversionDictionary[currentUnit]
                if newUnit not in conversionConstantsArray: #The convertToUnit does not exist.
                    newValue = value
                    if currentUnit != "word": # Will not print if it's "word" unit because frequently non-unit words are given as units
                        print("ERROR: Could not convert from %s to %s"%(currentUnit, newUnit))
                else:
                    newValue = value * float(conversionConstantsArray[newUnit.lower()])
            else: #It is not a primary unit so we need to find out what type of unit it is
                primaryUnit = self.getPrimaryUnit(currentUnit)
                if primaryUnit is not None: #convert to the primary unit before converting the next unit
                    unitToPrimary = float((1/self.conversionDictionary[primaryUnit][currentUnit]))
                    primaryValue = value * unitToPrimary
                    newValue = self.convertUnit(primaryValue, primaryUnit, newUnit)
                else:
                    newValue = None
        return newValue

    def getPrimaryUnit(self, unit):
        """
        returns the primary unit
        will return None if not in ConversionDictionary
        """
        returnPrimaryUnit = None
        for primaryUnit, unitTable in self.conversionDictionary.items():
            if unit in unitTable:
                returnPrimaryUnit = primaryUnit
                break
        return returnPrimaryUnit

##Tester
if __name__ == '__main__': # if someone directly ran this script rather than importing it, run the algos
    conversionCounter = 0
    unitConversionTable = UnitConversionTable()
    while conversionCounter == 0 or input("continue ").find("y") >= 0:
        currentUnit = input("What is your current unit? ")
        newUnit = input("What is your new unit? ")
        value = input( "What is the value? " )
        print("Converted Value from " + currentUnit + " to " + newUnit + ": ", unitConversionTable.convertUnit(value, currentUnit, newUnit))
        conversionCounter += 1
