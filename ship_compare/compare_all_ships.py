import sys
sys.path.insert(0, "A:\DevenirProjectsA")
from ABoatScraping.ABoatDatabase import BoatDatabase
from ABoatScraping.ship_compare.compare_ship_to_database import DatabaseCompare
from ABoatScraping import Config

"""A script that will compared all edges in the database. will override existing edges"""
settingsPath = "A:/DevenirProjectsA/ABoatScraping/shipSettings.json" #use default settings
settings = Config.getConfigFromPath(settingsPath)
databaseIp = settings["dbIp"]
databasePort = int(settings["dbPort"])
boatDatabase = BoatDatabase(databaseIp, databasePort)
filter = {}
allShips = boatDatabase.findShips(filter)

startingCompareShipIndex = 0
for ship in allShips:
    """"will redundantly create edges because they are not directed. We care about edge COMBINATIONS not PERMUTATIONS (ignore order).
    Nonetheless, because the way the other script is set up, the redudant edges will also be calculated.
    These redudant edges will just override the existing edge, so it won't actually affect the graph. Nonetheless, this should be changed at some point in time
    for efficiency sake."""
    compareToDatabase = DatabaseCompare(ship)
    compareToDatabase.writeEdgesToDatabase() # Writes the edges to the database
    compareToDatabase.closeDatabases()
