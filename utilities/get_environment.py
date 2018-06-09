import os
from ABoatScraping import UnitConversionTable
PACKAGE_PATH = os.path.dirname(UnitConversionTable.__file__)
CONFIG_PATH = PACKAGE_PATH + "/shipSettings.json"
RECOMMENDED_UNITS = {
    "displacement": "t",
    "length": "m",
    "beam": "m",
    "draft": "m",
    "speed": "kn",
    "range": "nmi"
}
