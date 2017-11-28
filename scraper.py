from lxml import cssselect
from lxml import html
from unidecode import unidecode
import requests
import json

def normalizeString(string, removeNewLines):
    if removeNewLines:
        string = string.replace("\n", " ") #replace new lines with spaces
    return unidecode(string)
def removeOddCharacters(string, charactersArray):
    for character in charactersArray:
        string = string.replace(character, "")
    return string
def formatString(string):
    oddCharacters = ['\"',':']
    string = normalizeString(string, True)
    return removeOddCharacters(string, oddCharacters)


def getArrayOfWords(haystack, needle, numberOfWords): #number of words including needle
    words = []
    position = haystack.find(needle)
    while position != -1 and len(words) < numberOfWords:
        haystack = haystack[position:]

        #check for more than one space and remove them if they exist (AKA if there is a space at the position index)
        while haystack[0:1] == ' ':
            haystack = haystack[1:]


        positionOfNextSpace = haystack.find(" ")

        if positionOfNextSpace == -1:
            word = haystack
            position = positionOfNextSpace
        else:
            word = haystack[0 : positionOfNextSpace]
            position = positionOfNextSpace + 1
        words.append(word)
    return words
def processRow(rowElement, shipBeingUpdated):
    cellElements = rowElement.cssselect("td")
    if len(cellElements) == 2:
        key = formatString(cellElements[0].text_content())
        valueElement = cellElements[1]
        arrayValueElements = valueElement.cssselect("ul>li")
        if len(arrayValueElements)==0: #dealing with a single value element aka not an array
            shipBeingUpdated[key] = formatString(valueElement.text_content())
        else :
            valuesArray = []
            for arrayValueElement in arrayValueElements:
                value = formatString(arrayValueElement.text_content())
                valuesArray.append(value)
            shipBeingUpdated[key] = valuesArray
    return shipBeingUpdated

shipPages = ["https://en.wikipedia.org/wiki/USS_Iowa_(BB-61)"]
ships = []
for pageURL in shipPages:
    ship = {}
    page = requests.get(pageURL)
    tree = html.fromstring(page.content)
    infoBox = tree.cssselect(".infobox")[0]
    content = tree.cssselect("#bodyContent")[0]
    #Scrapes ship name
    ship["name"] = tree.cssselect("#firstHeading")[0].text_content()
    shipImages = []

    #Scrapes all images and descriptions
    images = content.cssselect("img")
    for image in images:
        imageObject = {}
        src = image.attrib["src"]
        description = image.attrib["alt"]
        imageObject["src"] = src
        imageObject["description"] = description
        if len(description)>0: #Filters out non-ship related pictures
            shipImages.append(imageObject)

    ship["pictures"] = shipImages

    #get most ship infoBox
    rows = infoBox.cssselect("tr")
    for row in rows:
        ship = processRow(row, ship)


    #print (infoBox.text_content())


    #Appends the ship to the list of ships
    ships.append(ship)
print(json.dumps(ships))
