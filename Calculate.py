import math
class Calculate(object):
    sortedValues = []
    def __init__(self, arrayOfValues):
        self.sortedValues = arrayOfValues
        self.sortedValues.sort() #will also sort the values array being sent
    def addValue(self, value):
        """Add a value to the array of values for calculations to be performed on"""
        minIndex = 0
        maxIndex = len(self.sortedValues)
        self.addValueBinary(value, minIndex, maxIndex)

    def findMedian(self):
        median = None
        sortedValues = self.sortedValues
        length = len(sortedValues)
        if length % 2 == 0: #there is no middle value because the list size is even. average the two middle elements
            upperMiddleIndex = int(length / 2)
            sumOfMiddleElements =  sortedValues[upperMiddleIndex - 1] + sortedValues[upperMiddleIndex]
            median = sumOfMiddleElements / 2
        else: #the list size is odd, which means there is a middle element
            middleIndex = math.floor(length / 2) #because odd and 0 is the first index, not one
            median = sortedValues[middleIndex]
        return median


    def addValueBinary(self, value, minIndex, maxIndex):
        """Used to add a value to the sorted array
           Length should be an int
           Uses binary search
        """
        middleIndex = minIndex + math.ceil((maxIndex - minIndex) / 2)
        if minIndex == maxIndex:
            if middleIndex == len(self.sortedValues) or self.sortedValues[middleIndex] > value: #if it equals the length, then don't check to see if another element is at that index
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





values = [7, 2, 3, 1, 4, 5]
calculateObject = Calculate(values)
print("SORTED: ", calculateObject.sortedValues)
print("Median", calculateObject.findMedian())
print("Adding values...")

calculateObject.addValue(8)
calculateObject.addValue(7)
calculateObject.addValue(3.3)
calculateObject.addValue(-1)


calculateObject.addValue(0)


print("SORTED: ", calculateObject.sortedValues)
print("Median", calculateObject.findMedian())
