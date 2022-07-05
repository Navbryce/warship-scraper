from os import path

CONFIG_PATH = path.join(path.dirname(__file__),  "../../shipSettings.json")
RECOMMENDED_UNITS = {
    "displacement": "t",
    "length": "m",
    "beam": "m",
    "draft": "m",
    "speed": "kn",
    "range": "nmi"
}
