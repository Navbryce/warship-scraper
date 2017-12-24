

class UnitConversionTable(object):
    ""
    conversionDictionary = {};




    def __init__(self):
        #First Key: "What you are converting from". Second Key: "What you are converting to". #mm is the primary unit we want to use, so everything will be able to convert to (and from it)
        self.conversionDictionary = {
            'mm': {
                'cm': .1,
                'in': .0393701,
                'm': .001
            }
        }

    def convertUnit(self, value, currentUnit, newUnit):
        """Returns float"""

        value = float(value)
        newValue = None
        if currentUnit == newUnit:
            newValue = value
        else:
            if currentUnit in self.conversionDictionary: #we can convert directly because currentUnit is a primary unit
                conversionConstantsArray = self.conversionDictionary[currentUnit]
                newValue = value * float(conversionConstantsArray[newUnit])
            else: #It is not a primary unit so we need to find out what type of unit it is
                unitCategory = self.getUnitCategory(currentUnit)
                if unitCategory == "length": #convert to millimeters, a primary value, so we can convert to everything else
                    unitToMilli = float((1/self.conversionDictionary['mm'][currentUnit]))
                    mmValue = value * unitToMilli
                    newValue = self.convertUnit(mmValue, 'mm', newUnit)
                else:
                    newValue = None
        return newValue

    def getUnitCategory(self, unit):
        unitType = None
        if unit in self.conversionDictionary['mm']: #there is a key for the "unit" in the length tab, so it must be a length value
            unitType = "length"
        if unitType == None:
            unitType = None #Deal with other kinds of units

        return unitType

##Tester
"""
conversionCounter = 0
unitConversionTable = UnitConversionTable()
while conversionCounter == 0 or input("continue ").find("y") >= 0:
    currentUnit = input("What is your current unit? ")
    newUnit = input("What is your new unit? ")
    value = input( "What is the value? " )
    print("Converted Value from " + currentUnit + " to " + newUnit + ": ", unitConversionTable.convertUnit(value, currentUnit, newUnit))
    conversionCounter += 1
"""
