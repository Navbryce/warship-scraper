from datetime import datetime

class Date(datetime):
    def toSerializableForm(self):
        dateDictionary = {}
        if self.day is not None:
            dateDictionary = {'day': self.day}
        if self.month is not None:
            dateDictionary = {'month': self.month}
        if self.year is not None:
            dateDictionary = {'year': self.year}

        return dateDictionary
