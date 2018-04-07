import sys
import os
ship_scraping_path = os.environ.get('SHIP_SCRAPER') # check environment variable. if not set, use a default value
if ship_scraping_path is None:
    ship_scraping_path = "A:\DevenirProjects"
else:
    ship_scraping_path += '/..'
sys.path.insert(0, ship_scraping_path)
from ABoatScraping.ABoatDatabase import BoatDatabase
from ABoatScraping.ship_compare.compare_ship_to_database import DatabaseCompare
from ABoatScraping import Config
from ABoatScraping.utilities.get_environment import CONFIG_PATH

"""A script that will compared all edges in the database. will override existing edges"""
settings = Config.getConfigFromPath(CONFIG_PATH)
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
