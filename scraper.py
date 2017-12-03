from lxml import cssselect
from Armament import Armament
from lxml import html
from unidecode import unidecode
import requests
import json

def normalizeString(string, removeNewLines):
    if removeNewLines:
        string = string.replace("\n", " ") #replace new lines with spaces
    return unidecode(string) #Converts unicode characters to normal characters
def removeOddCharacters(string, charactersArray):
    for character in charactersArray:
        string = string.replace(character, "")
    return string
def formatString(string):
    oddCharacters = ['\"',':']
    string = normalizeString(string, True)
    return removeOddCharacters(string, oddCharacters)
def getWordsBeforeUnit(haystack, unit, numberOfWords):
    unit = ' ' + unit   #ensures it's not just part of word
    words = []
    positionOfUnit = haystack.find(unit)
    if positionOfUnit != -1:
        haystack = haystack[0:positionOfUnit] #really crops out the space before the unit and everyhthing eafter
        mostRecentSpace =  len(haystack)
        position = mostRecentSpace - 1
        while len(words) < numberOfWords and position != -1:
            character = haystack[position]
            if character == ' ':
                if position + 1 != mostRecentSpace: #makes sure it isn't just a space before a space
                    word = haystack[position + 1:] #The indexes after the space to the end of the string should all be words
                    words.append(word)
                haystack = haystack[0:position] #crops out the space
                mostRecentSpace = len(haystack)
            elif position == 0:
                word = haystack[position:] #The indexes after the space to the end of the string should all be words
                words.append(word)

            position-=1;
    return words



def getArrayOfWords(haystack, needle, numberOfWords): #number of words including needle. if needle is None, then start at beginning of haystack. if numberOfWords==-1, then all words
    words = []
    if needle:
        position = haystack.find(needle)
    else:
        position = 0
    while position != -1 and (len(words) < numberOfWords or numberOfWords == -1):
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
def processArmament(armamentElement):
    armament = None
    arrayOfWords = getArrayOfWords(formatString(armamentElement.text_content()), None, -1)
    if(len(arrayOfWords) > 1): #if it equals 1, then it's a date (extraneous, not armament, date of gun configuration)
        armamentLink = armamentElement.cssselect('a')[0]; #there should be one and only one link in an armament element. the link should be the full name of the gun
        armamentFullName = formatString(armamentLink.text_content());

        armament = Armament(armamentFullName, arrayOfWords[0])


        charactersToRemove = ['(', ')']
        armamentFullNameWithout = removeOddCharacters(armamentFullName, charactersToRemove)
        unitsToTry = ["mm", "cm"] #Prioritizes the first in the array
        for unit in unitsToTry:
            armamentSizeArray = getWordsBeforeUnit(armamentFullNameWithout, unit, 1)
            if len(armamentSizeArray) == 1:
                armament.size = armamentSizeArray[0]
                armament.sizeUnit = unit
                break #You want to prioritze the first unit


        armament = armament.toSerializableForm()
    return armament


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
            if key == "Armament":
                configuration = 2 #Which configuration do you want if their are multiple configurations
                configurationCounter = 0
                armamentElementCounter = 0
                oneConfiguration = False #If there is only one configuration, keep all armaments. The counter increments the configuration counter by one when it runs into its first null (a date) because if there are two configurations, both have a dates. 1st configuration is after the FIRST null except for when there is only ONE configuration (no dates, no nulls)

                for arrayValueElement in arrayValueElements:
                    value = processArmament(arrayValueElement)
                    if value != None and armamentElementCounter == 0: #The first "value" is not a configuration year, so it must only have one configuration
                        oneConfiguration = True
                    elif value is None:
                        configurationCounter += 1


                    if configurationCounter > configuration:
                        break
                    elif (configurationCounter == configuration and value != None) or (oneConfiguration):
                        valuesArray.append(value)

                    armamentElementCounter += 1

            else:
                for arrayValueElement in arrayValueElements:
                    value = formatString(arrayValueElement.text_content())
                    valuesArray.append(value)
            shipBeingUpdated[key] = valuesArray
    return shipBeingUpdated

shipPages = ["https://en.wikipedia.org/wiki/USS_Iowa_(BB-61)", "https://en.wikipedia.org/wiki/German_battleship_Gneisenau"]
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
