class Edge(object):
    def __init__(self, source, target, intialMagnitude = 1, reasons = ["No reason provided"]):
        """ reasons should be an array of strings """
        self.source = source
        self.target = target
        self.magnitude = intialMagnitude
        self.reasons = reasons

    def incrementMagnitude(self, magnitude_increment, reasons):
        """ reasons should be an array of strings """
        self.magnitude += magnitude_increment
        self.reasons += reasons
        return self.magnitude

    def toSerializableForm(self):
        """ Returns python dictionary """
        return {
            'source': self.source,
            'target': self.target,
            'magnitude': self.magnitude,
            'reasons': self.reasons
        }
