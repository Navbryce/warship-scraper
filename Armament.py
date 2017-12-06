class Armament(object):
    numberOfBarrels = -1
    fullName = None
    unit = None
    size = None


    def __init__(self, fullName, numberOfBarrels):
        self.fullName = fullName
        self.numberOfBarrels = numberOfBarrels
    def toSerializableForm(self):
        armament = {'fullName': self.fullName,
                    'numberOfBarrels': self.numberOfBarrels}
        if self.size != None:
            armament['size'] = self.size
            armament['unit'] = self.unit
        return armament
