import sys
import traceback
import os
ship_scraping_path = os.environ.get('SHIP_SCRAPER') # check environment variable. if not set, use a default value
if ship_scraping_path is None:
    ship_scraping_path = "A:\DevenirProjects"
else:
    ship_scraping_path += '/..'
sys.path.insert(0, ship_scraping_path)

from ABoatScraping.ABoatDatabase import BoatDatabase
from ABoatScraping.ship_compare.edge_database import EdgeDatabase
from ABoatScraping import Config
from ABoatScraping.utilities.get_environment import CONFIG_PATH

settings = Config.getConfigFromPath(CONFIG_PATH)
databaseIp = settings["dbIp"]
databasePort = int(settings["dbPort"])

# GET SETTINGS through parameters passed to script
runScript = True
try:
    if len(sys.argv) != 2: #the script name is always the first argument
        print("TEST")

        print("An error occurred with the parameter(s) you entered, so the script will not be run")
        print("Please pass: {scrapeURL}")
        runScript = False
except Exception as exception:
    print("An error occurred with the parameter(s) you entered, so the script will not be run")
    print("Please pass: {scrapeURL}")
    print(exception) #Print exception because when running child process from node, only output directly printed to console can be seen
    traceback.print_exc()
    runScript = False

if runScript:
    scrapeURL = sys.argv[1]
    print("Deleting ship/edges with " + scrapeURL + " as a scrapeURL/target/source")
    shipDatabaseFilter = {"scrapeURL": scrapeURL}

    shipDatabase = BoatDatabase(databaseIp, databasePort)
    shipsDeleted = shipDatabase.deleteShips(shipDatabaseFilter)
    print("# of Deleted Ship(s) -- should only be one: ", shipsDeleted.deleted_count)
    shipDatabase.closeConnection()

    edgesDatabaseFilter = {"$or": [
        {"target": scrapeURL},
        {"source": scrapeURL}
    ]}

    edgesDatabase = EdgeDatabase(databaseIp, databasePort)
    edgesDeleted = edgesDatabase.deleteEdges(edgesDatabaseFilter)
    print("# of Deleted Edge(s): ", edgesDeleted.deleted_count)
    edgesDatabase.closeConnection()
