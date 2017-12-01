import json

class Armament(object):
    numberOfBarrels = -1
    fullName = None


    def __init__(self, fullName, numberOfBarrels):
        self.fullName = fullName
        self.numberOfBarrels = numberOfBarrels
    def toSerializableForm(self):
        armament = {'fullName': self.fullName,
                    'numberOfBarrels': self.numberOfBarrels}
        return armament
