class Armament(object):
    numberOfBarrels = -1
    fullName = None
    unit = None
    size = None
    isMissile = None
    isCannon = False


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
    def isCannonCheck(self): #is not called in a constructor because the unit is necessary.
        """
        Can only be called if unit has been set
        Will return false if no unit
        """
        isCannon = False
        if self.unit is not None:
            isCannon = self.unit == "pounder"
            self.isCannon = isCannon
        return isCannon

    def toSerializableForm(self):
        armament = {'fullName': self.fullName,
                    'quantity': int(self.numberOfBarrels),
                    }
        if self.size != None:
            armament['size'] = float(self.size)
            armament['unit'] = self.unit
            armament['isCannon'] = self.isCannonCheck()
            armament['isMissile'] = self.isMissile
        return armament
