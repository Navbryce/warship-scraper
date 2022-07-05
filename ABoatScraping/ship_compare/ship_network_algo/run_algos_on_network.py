from ABoatScraping.ABoatDatabase import BoatDatabase
from ABoatScraping.ship_compare.edge_database import EdgeDatabase
from ABoatScraping.ship_compare.ship_network_algo.shortest_path import getDistancesAndWriteToDatabase
from ABoatScraping.utilities.get_environment import CONFIG_PATH
from ABoatScraping import Config

def run_algos():
    settings = Config.getConfigFromPath(CONFIG_PATH)

    # Run this script to run important algos on the entire network, such as distance algo

    # Shortest path algo. Function will automatically write distances to ship collection under "distances" property
    maximum_magnitude = 50 # maximum edge magnitude.the strongest possible connection strength. Does NOT represent cost or distance. Cost or distance is: 1 - (maginitude/maximumMagnitude)
    boatDatabase = BoatDatabase()
    edgeDatabase = EdgeDatabase()
    # PARELLIZE the code below. run a new thread for each ship
    for ship in boatDatabase.findShips({}): # goes through every ship and finds the distances to all other ships for each ship. will write to each to the ships collection.
        scrapeURL = ship["scrapeURL"]
        getDistancesAndWriteToDatabase(scrapeURL, boatDatabase, edgeDatabase, maximum_magnitude)

    boatDatabase.closeConnection()
    edgeDatabase.closeConnection()
if __name__ == '__main__': # if someone directly ran this script rather than importing it, run the algos
    run_algos()
