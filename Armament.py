class Armament(object):
    numberOfBarrels = -1
    fullName = None
    unit = None
    size = None
    isMissile = None


    def __init__(self, fullName, numberOfBarrels):
        self.fullName = fullName
        self.numberOfBarrels = numberOfBarrels
        self.isMissile = self.isMissileCheck(fullName)

    def isMissileCheck(self, fullName):
        isMissile = False
        missileKeysWords = ['missile']
        for keyword in missileKeysWords:
            isMissile = fullName.find(keyword) >= 0
            if (isMissile):
                break
        return isMissile
    def toSerializableForm(self):
        armament = {'fullName': self.fullName,
                    'quantity': self.numberOfBarrels,
                    'isMissile': self.isMissile
                    }
        if self.size != None:
            armament['size'] = self.size
            armament['unit'] = self.unit
        return armament
