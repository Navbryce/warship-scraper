from lxml import cssselect
from Armament import Armament
from Armor import Armor
from lxml import html
from Date import Date
from unidecode import unidecode
import requests
import json

#Global variables
previousArmorType = None


def normalizeString(string, removeNewLines):
    if removeNewLines:
        string = string.replace("\n", " ") #replace new lines with spaces
    return unidecode(string) #Converts unicode characters to normal characters

def removeOddCharacters(string, charactersArray):
    for character in charactersArray:
        string = string.replace(character, "")
    return string
def replaceOddCharacters(string, oddCharacters, replaceCharacter):
    for oddCharacter in oddCharacters:
        string = string.replace(oddCharacter, replaceCharacter)
    return string
def replaceColonWithSpace(string):
    oddCharacters = [":"]
    return replaceOddCharacters(string, oddCharacters, " ")
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

            position-=1
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

#Returns a Date object. Assumes the date is in the "day month year" format
def createDateObject(dateString):
    return Date.strptime(dateString, "%d %B %Y")

def processArmament(armamentElement):
    armament = None
    arrayOfWords = getArrayOfWords(formatString((armamentElement.text_content())), None, -1)
    if(len(arrayOfWords) > 1): #if it equals 1, then it's a date (extraneous, not armament, date of gun configuration)
        armamentLink = armamentElement.cssselect('a')[0] #there should be one and only one link in an armament element. the link should be the full name of the gun
        armamentFullName = formatString(armamentLink.text_content())

        armament = Armament(armamentFullName, arrayOfWords[0])


        charactersToRemove = ['(', ')']
        armamentFullNameWithout = removeOddCharacters(armamentFullName, charactersToRemove)
        unitsToTry = ["mm", "cm"] #Prioritizes the first in the array
        for unit in unitsToTry:
            armamentSizeArray = getWordsBeforeUnit(armamentFullNameWithout, unit, 1)
            if len(armamentSizeArray) == 1:
                armament.size = armamentSizeArray[0]
                armament.unit = unit
                break #You want to prioritze the first unit


        armament = armament.toSerializableForm()
    return armament

def processArmor(armorElement):
    global previousArmorType

    armor = None
    armorRange = False
    armorMinValue = None
    armorMaxValue = None
    armorUnit = None
    armorType = None

    armorFormattedText = formatString(replaceColonWithSpace((armorElement.text_content()))) #replace colon with space because some pages have errors where there is no space after the colon
    arrayOfWords = getArrayOfWords(armorFormattedText, None, 10)
    if len(arrayOfWords) >= 1:
        armorType = arrayOfWords[0]
        dealingWithSubItem = False; #IF dealing with the item under a list of armor types that is only part of an armor type. AKA "deck": "first", "second". "third"
        if(len(arrayOfWords) >= 2):#FILTERS OUT: We are dealing with the title to a list of armor elements below this one
            oddCharacters = ["(", ")"]
            armorFullName = removeOddCharacters(armorFormattedText, oddCharacters)

            units = ["mm"]
            for unit in units:
                armorWidthArray = getWordsBeforeUnit(armorFullName, unit, 3) #Get three because a possible situation: {min} to {max}
                if len(armorWidthArray)>1:
                    armorUnit = unit
                    if len(armorWidthArray) == 3 and armorWidthArray[1] == "to": #If there aren't three words, that means it's impossible for it to be a range. @ Index 1 is where "to" should be
                        armorRange = True
                        armorMaxValue = armorWidthArray[0] #0 is the first word before the unit
                        armorMinValue = armorWidthArray[2] #2 is the third word after the unit
                    else:
                        armorMaxValue = armorWidthArray[0]
                        armorMinValue = armorWidthArray[0]

                    if previousArmorType != None and len(armorElement.cssselect("a")) == 0: #you can identify a sub list item by its LACK of a link
                        armorType = previousArmorType + " " + armorType #previousArmorType is the title of the list such as "Deck" in "Deck": "First", "Second"
                        dealingWithSubItem = True

                    armor = Armor(armorType, armorMinValue, armorMaxValue, armorUnit, armorRange)

                    break #exit the unit for loop
        if dealingWithSubItem is False:
            previousArmorType = armorType  #global variable defined in processArmor scope

    armorSerializable = None
    if armor != None:
        armorSerializable = armor.toSerializableForm()
        #print(armorSerializable)
    return armorSerializable

def categorizeElement(key, value, ship): #Will categorize elements that are not already in "arrays." For example, commissioned, decomissioned, recomissioned, ... are all listed as separate elements in the highest level of table
    key = key.lower() #the key value is the key in the highest level of the info table

    #Find the category that applies
    importantDateKeyWords = ['commission', 'launch', 'struck', 'laid', 'ordered']
    importantDate = False
    for keyWord in importantDateKeyWords: #If else separate from for loop for organizational reasons rather. I didn't want a bunch of nested for loops and if statements
        if key.find(keyWord) >= 0:
            importantDate = True
            break

    #Add element to category. Perform necessary operations
    if importantDate:
        if 'importantDates' not in ship: #creates the array if it doesn't already exist
            ship['importantDates'] = []
        dateElement = {"significance": key, "date": createDateObject(value).toSerializableForm()}
        ship['importantDates'].append(dateElement)
    else:   #Catch all
        ship[key] = value
    return ship

def processRow(rowElement, shipBeingUpdated):
    cellElements = rowElement.cssselect("td")
    if len(cellElements) == 2 and len(cellElements[1].cssselect('img')) == 0: #Ensure it actually has a value and the value does not have a nimage
        key = formatString(cellElements[0].text_content())
        valueElement = cellElements[1]
        arrayValueElements = valueElement.cssselect("ul>li")
        if len(arrayValueElements)==0: #dealing with a single value element aka not an array
            shipBeingUpdated = categorizeElement(key, formatString(valueElement.text_content()), ship)
        else :
            valuesArray = []
            if key == "Armament":
                configuration = int(shipBeingUpdated['configuration']) #Which configuration do you want if their are multiple configurations
                configurationCounter = -1 #If multiple configurations, the first one will have a date at the top of it
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

            elif key == "Armor":
                previousArmorType = None
                for armorElement in arrayValueElements:
                    armor = processArmor(armorElement)
                    if armor != None:
                        valuesArray.append(armor)

            else:
                for arrayValueElement in arrayValueElements:
                    value = formatString(arrayValueElement.text_content())
                    valuesArray.append(value)

            shipBeingUpdated[key] = valuesArray
    return shipBeingUpdated


#Main script
shipPages = [
                {"url": "https://en.wikipedia.org/wiki/USS_Iowa_(BB-61)", "configuration": "0"},
                {"url": "https://en.wikipedia.org/wiki/German_battleship_Gneisenau", "configuration": "0"}
            ]
ships = []
maxNumberOfImagesForAShip = 5
for page in shipPages:
    #Parrellize ?
    ship = {'configuration': page['configuration']}
    page = requests.get(page['url'])
    tree = html.fromstring(page.content)
    infoBox = tree.cssselect(".infobox")[0]
    content = tree.cssselect("#bodyContent")[0]
    #Scrapes ship name
    ship["name"] = tree.cssselect("#firstHeading")[0].text_content()
    shipImages = []

    #Scrapes all images and descriptions
    images = content.cssselect("img")
    imageCounter = 0
    for image in images:
        imageObject = {}
        src = image.attrib["src"]
        description = image.attrib["alt"]
        imageObject["src"] = src
        imageObject["description"] = description
        if len(description)>0: #Filters out non-ship related pictures
            shipImages.append(imageObject)

        imageCounter += 1
        if imageCounter == maxNumberOfImagesForAShip:
            break


    ship["pictures"] = shipImages

    #get most ship infoBox
    rows = infoBox.cssselect("tr")
    for row in rows:
        ship = processRow(row, ship)


    #print (infoBox.text_content())


    #Appends the ship to the list of ships
    ships.append(ship)
print(json.dumps(ships))
