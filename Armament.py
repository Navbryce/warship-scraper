import json

class Armament(object):
    numberOfBarrels = -1
    numberOfTurrets = -1


    def __init__(self, numberOfBarrels):
        self.numberOfBarrels = numberOfBarrels
    def toSerializableForm(self):
        armament = {'numberOfBarrels': self.numberOfBarrels};
        return armament
