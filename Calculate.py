import math
class Calculate(object):
    sortedValues = []
    frequencies = {}
    currentMode = None
    sum = 0
    def __init__(self, arrayOfValues):
        self.frequencies = {}
        self.currentMode = None
        self.sum = 0

        self.sortedValues = arrayOfValues
        self.sortedValues.sort() #will also sort the values array being sent
        for value in arrayOfValues:
            self.sum += value
            self.addFrequency(value)

    # Static Methods
    @staticmethod
    def withinTolerance(firstValue, secondValue, tolerance):
        """
        tolerance should be a percent in the form of a decimal
        firstValue and secondValue should be floats
        returns true if second value is within tolerance of first value
        """
        delta = abs(secondValue - firstValue)
        # ORDER of firstValue and secondValue slightly matters when doing. Probably should be changed to some tyope of comparison where order does NOT matter
        if firstValue != 0:
            withinTolerance = delta/firstValue <= tolerance
        elif secondValue != 0:
            withinTolerance = delta/secondValue <= tolerance
        else:
            withinTolerance = True # they're both zero
        return withinTolerance

    @staticmethod
    def withinRange(firstValue, secondValue, range):
        """
        range is the maximum distance from the firstValue (+-)
        returns true if the second value is within the range AKA max distance of the first value
        """
        delta = abs(secondValue - firstValue)
        return delta <= range


    #ACCOUNT FOR QUANTITY
    def addValue(self, value):
        """Add a value to the array of values for calculations to be performed on"""
        value = float(value)

        minIndex = 0
        maxIndex = len(self.sortedValues) - 1
        self.addValueBinary(value, minIndex, maxIndex)
        self.sum += value
        self.addFrequency(value)

    #Normal Methods

    def addValueWithQuantity(self, value, n):
        """Will add the value n times"""
        value = float(value)
        n = int(n)
        while n > 0:
            self.addValue(value)
            n -= 1

    def addFrequency(self, value):
        """Increments frequency for value. Also checks to see if it is the new mode. Should never be called outside of this object. Not public"""
        #Deal with frequences (for mode)
        if value in self.frequencies:
            currentFrequency = self.frequencies[value]
        else:
            currentFrequency = 0
        self.frequencies[value] = currentFrequency + 1
        if self.currentMode == None or self.frequencies[value] > self.frequencies[self.currentMode]: #Checks to see if there is a new mode
            self.currentMode = value

    def findMode(self):
        """Finds the mode using the frequencies dictionary.
        and the currentMode private variable"""
        if self.currentMode is None:
            return -1
        else:
            return {
                "value": self.currentMode,
                "frequency": self.frequencies[self.currentMode]
            }

    def findMedian(self):
        median = None
        sortedValues = self.sortedValues
        length = len(sortedValues)
        if length == 0:
            median = -1
        elif length % 2 == 0: #there is no middle value because the list size is even. average the two middle elements
            upperMiddleIndex = int(length / 2)
            sumOfMiddleElements =  sortedValues[upperMiddleIndex - 1] + sortedValues[upperMiddleIndex]
            median = sumOfMiddleElements / 2
        else: #the list size is odd, which means there is a middle element
            middleIndex = math.floor(length / 2) #because odd and 0 is the first index, not one
            median = sortedValues[middleIndex]
        return median
    def calculateAverage(self):
        numberOfTerms = len(self.sortedValues)
        if numberOfTerms > 0:
            average = self.sum / numberOfTerms
        else:
            average = 0
        return average
    def getMinValue(self):
        return self.sortedValues[0]
    def getMaxValue(self):
        return self.sortedValues[len(self.sortedValues) - 1]
    def addValueBinary(self, value, minIndex, maxIndex):
        """Used to add a value to the sorted array
           Length should be an int
           Uses binary search
        """
        #print("Value: ", value, "Index: ", minIndex, "-", maxIndex, "Array: ",self.sortedValues)
        middleIndex = minIndex + math.ceil((maxIndex - minIndex) / 2)
        if minIndex >= maxIndex or middleIndex >= len(self.sortedValues):
            if middleIndex >= len(self.sortedValues):
                self.sortedValues.append(value)
            elif self.sortedValues[middleIndex] > value: #if it equals the length, then don't check to see if another element is at that index
                self.sortedValues.insert(middleIndex, value) #insert pushes the current value at that index up an index
            else:
                self.sortedValues.insert(middleIndex + 1, value)
        elif self.sortedValues[middleIndex] == value:
            self.sortedValues.insert(middleIndex + 1, value) #pushes the next value up
        else:
            if self.sortedValues[middleIndex] < value:
                minIndex = middleIndex + 1
            else:
                maxIndex = middleIndex - 1

            self.addValueBinary(value, minIndex, maxIndex)

    def calculationsDictionary(self):
        #Will return a dictionary with the mode, median, and average
        if len(self.sortedValues) > 0:
            objectToReturn = {
                "noValues": False,
                "sum": self.sum,
                "mode": self.findMode(),
                "median": self.findMedian(),
                "average": self.calculateAverage(),
                "minValue": self.getMinValue(),
                "maxValue": self.getMaxValue(),
                'numberOfValues': len(self.sortedValues)
            }
        else:
            objectToReturn =  { #Easier to have a boolean than an empty object for the GUI
                "noValues": True
            }
        return objectToReturn





"""
values = [7, 2, 3, 1, 4, 5]
calculateObject = Calculate(values)
print("SORTED: ", calculateObject.sortedValues)
print("Median", calculateObject.findMedian())
print("Mode", calculateObject.findMode())
print("Average", calculateObject.calculateAverage())

print("Adding values...")

calculateObject.addValue(8)
calculateObject.addValue(7)
calculateObject.addValue(3.3)
calculateObject.addValue(-1)


calculateObject.addValue(0)



print("SORTED: ", calculateObject.sortedValues)
print("Median", calculateObject.findMedian())
print("Mode", calculateObject.findMode())
print("Average", calculateObject.calculateAverage())

calculateObject.addValueWithQuantity(8, 5)



print("SORTED: ", calculateObject.sortedValues)
print("Median", calculateObject.findMedian())
print("Mode", calculateObject.findMode())
print("Average", calculateObject.calculateAverage())
"""
