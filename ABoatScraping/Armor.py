class Armor(object):
    armorType = None
    minValue = None
    maxValue = None
    unit = None
    range = None



    def __init__(self, armorType, minValue, maxValue, unit, range):
        self.armorType = armorType
        self.minValue = minValue
        self.maxValue = maxValue
        self.unit = unit
        self.range = range
    def toSerializableForm(self):
        armor = {
            'armorType': self.armorType,
            'minValue': self.minValue,
            'maxValue': self.maxValue,
            'unit': self.unit,
            'range': self.range
        }
        return armor
