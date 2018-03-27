import json
import math
import sys
sys.path.insert(0, "A:\DevenirProjectsA")
from ABoatScraping.ABoatDatabase import BoatDatabase
from ABoatScraping.ship_compare.edge_database import EdgeDatabase


def getDistancesFromNode(scrapeURL, nodes, max_magnitude, edge_database): # I keep switching between using camel case and underlines. I need to pick one
    """
        returns an array with the distances from the node submitted as an argument to all other nodes
        scrapeURL represents the scrapeURL of the node being observed
        max_magnitude represents the strong possible connection. Since weight represents cost in the alogirithim, weight is determined by magnitude 1 - (connection strength)/max_magnitude
    """
    max_magnitude = float(max_magnitude)

    distances = {}
    distances[scrapeURL] = 0 # the distance between a node and itself is 0

    nodesToFindPathsFor = []
    for node in nodes:
        if node != scrapeURL:
            distances[node] = math.inf
        nodesToFindPathsFor.append(node)


    while len(nodesToFindPathsFor) > 0:
        nodeWithSmallestDistanceIndex = getMinimumDistance(nodesToFindPathsFor, distances) # assumes this distance must be correct
        smallestScrapeURL = nodesToFindPathsFor[nodeWithSmallestDistanceIndex]
        nodesToFindPathsFor.pop(nodeWithSmallestDistanceIndex) # removes it from the array of finding paths for
        nodeNeighbors = edge_database.getNeighbors(scrapeURL)
        for neighbor in nodeNeighbors:
            # see function definition to understand
            scrapeURL = neighbor["scrapeURL"]
            magnitude = float(neighbor["magnitude"])
            distance = 1 - magnitude/max_magnitude # distance to node
            if distance < 0:
                distance = 0 # if the magnitude is greater than the magnitude (which it shouldn't be), treat it as 0
                print ("A magnitude for %s is greater than the max magnitude, so it the distance will be treated as 0"%(scrapeURL))
            possiblePath = distance + distances[smallestScrapeURL]

            if possiblePath < distances[scrapeURL]:
                distances[scrapeURL] = possiblePath
    return distances

def getMinimumDistance(nodesArray, dictWithDistances):
    """Returns the INDEX where the node with the smallest distance is in the nodesArray. Will return None if array is empty"""
    minimum = -1
    minimumIndex = None

    indexCounter = 0
    while indexCounter < len(nodesArray):
        scrapeURL = nodesArray[indexCounter]
        if (minimum == -1 or dictWithDistances[scrapeURL] < minimum):
            minimum = dictWithDistances[scrapeURL]
            minimumIndex = indexCounter
        indexCounter += 1
    return minimumIndex

def convertDistancesDictionary(distances):
    """Converts distances dictionary into a sorted array. The shorter the path, the stronger the connection"""
    distancesArray = []
    for scrapeURL, distance in distances.items():
        addDistanceBinary(scrapeURL, distance, 0, len(distancesArray) - 1, distancesArray)
    return distancesArray

def addDistanceBinary (scrapeURL, distance, minIndex, maxIndex, arrayOfDict):
    """Adds a distanceDict through binary search/add and recursion"""
    distanceDict = {
        "scrapeURL": scrapeURL,
        "distance": distance
    }
    value = distance

    middleIndex = minIndex + math.ceil((maxIndex - minIndex) / 2)
    if minIndex >= maxIndex or middleIndex >= len(arrayOfDict):
        if middleIndex >= len(arrayOfDict):
            arrayOfDict.append(distanceDict)
        elif arrayOfDict[middleIndex]["distance"] > value: #if it equals the length, then don't check to see if another element is at that index
            arrayOfDict.insert(middleIndex, distanceDict) #insert pushes the current value at that index up an index
        else:
            arrayOfDict.insert(middleIndex + 1, distanceDict)
    elif arrayOfDict[middleIndex]["distance"] == value:
        arrayOfDict.insert(middleIndex + 1, distanceDict) #pushes the next value up
    else:
        if arrayOfDict[middleIndex]["distance"] < value:
            minIndex = middleIndex + 1
        else:
            maxIndex = middleIndex - 1

        addDistanceBinary(scrapeURL, distance, minIndex, maxIndex, arrayOfDict)


# TEST SCRIPT
boatDatabase = BoatDatabase("localhost", 27017)
edgeDatabase = EdgeDatabase("localhost", 27017)
shipToFindPaths = "https://en.wikipedia.org/wiki/German_battleship_Scharnhorst"
maximumMagnitude = 13

nodes = []
for boat in boatDatabase.findShips({}):
    nodes.append(boat["scrapeURL"])
boatDatabase.closeConnection()
distances = getDistancesFromNode(shipToFindPaths, nodes, maximumMagnitude, edgeDatabase)
print("Distances", json.dumps(convertDistancesDictionary(distances)))
