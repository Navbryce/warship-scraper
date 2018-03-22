import hashlib

class Edge(object):
    def __init__(self, source, target, intialMagnitude = 1, reasons = ["No reason provided"]):
        """ reasons should be an array of strings """
        self.source = source
        self.target = target
        self.magnitude = intialMagnitude
        self.reasons = reasons
        self.id = self.generateID(self.source, self.target)

    def generateID(self, source, target):
        """generates a 'propertykey'. Essentially a key in the edges map (AKA python dictionary) """
        sourceHash = self.getHashForString(source)
        targetHash = self.getHashForString(target)
        return sourceHash*targetHash # ensures a unique value for each source, target combination THAT IS NOT dependent on which is source and which is hash. 

    def getHashForString(self, string):
        return int(hashlib.sha256(string.encode('utf-8')).hexdigest(), 16) % 10 ** 8 # shorten to 8 digit number because that's the max allowable by mongo

    def incrementMagnitude(self, magnitude_increment, reasons):
        """ reasons should be an array of strings """
        self.magnitude += magnitude_increment
        self.reasons += reasons
        return self.magnitude

    def toSerializableForm(self):
        """ Returns python dictionary """
        return {
            'edgeId': self.id,
            'source': self.source,
            'target': self.target,
            'magnitude': self.magnitude,
            'reasons': self.reasons
        }
