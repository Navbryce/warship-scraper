from datetime import datetime

class Date(datetime):
    def toSerializableForm(self):
        dateDictionary = {
            'day': self.day,
            'month': self.month,
            'year': self.year
        }
        return dateDictionary
