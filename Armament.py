class Armament(object):
    numberOfBarrels = -1
    fullName = None
    unit = None
    size = None
    isMissile = None
    isCannon = False
    isTorpedo = False


    def __init__(self, fullName, numberOfBarrels, unit, size):
        self.fullName = fullName
        self.numberOfBarrels = numberOfBarrels
        self.unit = unit
        self.size = size
        self.isMissile = self.isMissileCheck()
        self.isTorpedo = self.isTorpedoCheck()
        self.isCannon = self.isCannonCheck()

    def isMissileCheck(self):
        isMissile = False
        missileKeysWords = ['missile']
        for keyword in missileKeysWords:
            isMissile = self.fullName.find(keyword) >= 0
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
            cannonUnits = ["pounder", "kg"]
            for cannonUnit in cannonUnits:
                if self.unit == cannonUnit:
                    isCannon = True
                    break
            self.isCannon = isCannon
        return isCannon
    def isTorpedoCheck(self):
        """
        Can only be called if unit has been set
        Will return false if no unit
        """
        isTorpedo = False
        torpedoKeywords = ["torpedo"]
        for torpedoKeyword in torpedoKeywords:
            if self.fullName.find(torpedoKeyword) >= 0:
                isTorpedo = True
                break
        return isTorpedo

    def toSerializableForm(self):
        armament = {'fullName': self.fullName,
                    'quantity': int(self.numberOfBarrels),
                    }
        if self.size != None:
            armament['size'] = float(self.size)
            armament['unit'] = self.unit
            armament['isCannon'] = self.isCannon
            armament['isTorpedo'] = self.isTorpedo
            armament['isMissile'] = self.isMissile
        return armament
