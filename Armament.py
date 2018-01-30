class Armament(object):
    numberOfBarrels = -1
    unit = None
    size = None
    isMissile = None
    isCannon = False
    isTorpedo = False
    unknown = False


    def __init__(self, fullName, numberOfBarrels, unit = None, size = None):
        self.fullName = fullName
        self.lowerCaseName = self.fullName.lower(); # Stored along with the unalterted fullname because redoing caps in the visualizatoin is difficult because of acronyms vs standard words
        self.numberOfBarrels = numberOfBarrels
        self.isMissile = self.isMissileCheck()

        if unit is not None:
            self.unit = unit
            self.size = size
            self.isTorpedo = self.isTorpedoCheck()
            self.isCannon = self.isCannonCheck()
        elif self.isMissile:
            self.size = 0 #For some reason it couldn't find the missile size (they're not always listed. I will need to create a scraper to scrape the missile's page)
            self.unit = "mm"
        else:
            self.unknown = True

    def isMissileCheck(self):
        isMissile = False
        missileKeysWords = ['missile']
        for keyword in missileKeysWords:
            isMissile = self.lowerCaseName.find(keyword) >= 0
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
        torpedoKeywords = ["torpedo", "tubes"]
        for torpedoKeyword in torpedoKeywords:
            if self.lowerCaseName.find(torpedoKeyword) >= 0:
                isTorpedo = True
                break
        return isTorpedo

    def toSerializableForm(self):
        armament = {'fullName': self.fullName,
                    'quantity': int(self.numberOfBarrels),
                    'unknown': self.unknown
                    }
        if self.unknown is False: #unknown is true when no unit was sent and it's not a missile
            armament['size'] = float(self.size)
            armament['unit'] = self.unit
            armament['isCannon'] = self.isCannon
            armament['isTorpedo'] = self.isTorpedo
            armament['isMissile'] = self.isMissile

        return armament
