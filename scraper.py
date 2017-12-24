from lxml import cssselect
from Armament import Armament
from Armor import Armor
from lxml import html
from Date import Date
from UnitConversionTable import UnitConversionTable
from Calculate import Calculate
from unidecode import unidecode
import requests
import sys
import traceback
import json

#Global variables
global websiteRoot #Assigned in the settings area of the script
global conversionTable #ConversionTable


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
def isWordInt(word):
    """
    word - Word being observed
    If: the word is an int, the int will be returned
    Else: nothing will be returned
    """
    try:
        oddChracters = [","]
        word = removeOddCharacters(word, oddChracters)
        intObject = int(word)
    except:
        #traceback.print_exc()
        intObject = None
    return intObject

def parseIntFromStringArray(haystackArray, intToKeep):
    intCounter = -1
    """
    intToKeep -- 0: first int 1: second int
    Will return None if no int found
    """
    intObject = None
    for word in haystackArray:
        possibleInteger = isWordInt(word)
        if possibleInteger is not None:
            intObject = possibleInteger
            intCounter += 1
            if intCounter == intToKeep:
                break
    return intObject


def getWordsBeforeUnit(haystack, unit, numberOfWords):
    unit = ' ' + unit   #ensures it's not just part of word. in case it's at the end
    words = []
    positionOfUnit = haystack.find(unit) #because of the space
    unitLength = len(unit)

    while positionOfUnit != -1 and positionOfUnit + unitLength != len(haystack) and haystack[positionOfUnit + unitLength] != ' ': #makes sure the unit is by itself if not at the end of the string
        if haystack[positionOfUnit + 1:].find(unit) >= 0:
            positionOfUnit = positionOfUnit + 1 + haystack[positionOfUnit + 1:].find(unit)
        else:
            positionOfUnit = -1



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

def createStringFromArray(startingIndex, arrayOfWords): #creates string from array of words. first word is at starting index
    wordCounter = startingIndex
    string = ""
    while wordCounter < len(arrayOfWords):
        if wordCounter == len(arrayOfWords) - 1:
            string += arrayOfWords[wordCounter]
        else:
            string += arrayOfWords[wordCounter] + " "
        wordCounter += 1
    return string

def getArrayOfWords(haystack, needle, numberOfWords): #number of words including needle. if needle is None, then start at beginning of haystack. if numberOfWords==-1, then all words
    words = []
    if needle:
        position = haystack.find(needle)
    else:
        position = 0
    while position != -1 and (len(words) < numberOfWords or numberOfWords == -1):
        word = None


        haystack = haystack[position:]

        #check for more than one space and remove them if they exist (AKA if there is a space at the position index)
        while haystack[0:1] == ' ':
            haystack = haystack[1:]

        positionOfNextSpace = haystack.find(" ")

        if positionOfNextSpace == -1:
            if len(haystack) > 0:
                word = haystack
                words.append(word)
            position = positionOfNextSpace

        else:
            word = haystack[0 : positionOfNextSpace]
            words.append(word)
            position = positionOfNextSpace + 1
    return words

def getImages(pageElement, maxImages): #Page element = DOM element that is a parent (direct or indirect) of the pictures
    #Scrapes all images and descriptions
    imageObjArray = []
    imagesWrappers = pageElement.cssselect(".thumb")
    imageCounter = 0
    if maxImages > 0:
        for imageWrapper in imagesWrappers: #Image wrapper is the container for the caption and image

            images = imageWrapper.cssselect("img")
            if len(images) > 0:
                image = images[0] #Actual image object
                captions = imageWrapper.cssselect(".thumbcaption")
                if len(captions) > 0:
                    caption = captions[0] #Holds the description
                    description = formatString(caption.text_content())
                else:
                    description = "No description found"

                imageObject = {}
                src = image.attrib["src"][2:] #remove the first two characters of the URL because they are a filepaths for the server ('//'), not URL. Represent root.
                imageObject["src"] = "https://" + src
                imageObject["description"] = description
                if len(description)>0: #Filters out non-ship related pictures
                    #Filters out unwanted images such as "svgs"
                    filterOutKeyWords = ['svg']
                    containsKeyWord = False
                    for keyword in filterOutKeyWords:
                        if src.find(keyword) >= 0:
                            containsKeyWord = True
                    if containsKeyWord == False:
                        imageObjArray.append(imageObject)
                        imageCounter += 1
                        if imageCounter == maxImages:
                            break
    return imageObjArray
def getInfoBoxPicture(infobox):
    """returns picture object"""
    picture = infobox.cssselect("img")[0]
    src = "https://" + picture.attrib["src"][2:] #remove the first two characters of the URL because they are a filepaths for the server ('//'), not URL. Represent root.
    description = formatString(picture.attrib["alt"])
    pictureObject = {
        "src":  src,
        "description": description
    }
    return pictureObject

#Returns a Date object. Assumes the date is in the "day month year" format
def createDateObject(dateString):
    dateObject = None
    try:
        dateObject = Date.strptime(dateString, "%d %B %Y")
    except:
        try:
            dateObject = Date.strptime(dateString, "%B %Y")
        except:
            try:
                dateObject = Date.strptime(dateString, "%Y")
            except:
                print("A date object could not be created from the string: " + dateString)

    return dateObject

def processArmament(armamentElement, armamentString, arrayOfWords, armamentCalculateObjects):
    """
    armamentElement - the armament dom element
    armamentString and arrayOfWords - Array of words from armament. Sent as parameter because it is already "calcualted" when checking to see if the armament is a date
    armamentCalculateObject - A dictionary with a Calculate(.py) object for each type of armament. Used to calculate average, median, and related values for size and quantity. See processArmamentElements
    """
    pictures = []

    armament = None

    armamentLinks = armamentElement.cssselect('a')


    if len(armamentLinks) > 0:#Assumes the full name is contained within links if evaluates to true
        linkWordsArray = [] #each 'word' is probably a phrase
        linkCounter = 0
        for link in armamentLinks:
            linkWordsArray.append(formatString(link.text_content()))
            #GETS IMAGES for armament. Uses the last armament link if there are more than one.
            if linkCounter == len(armamentLinks) - 1:
                armamentPage = html.fromstring(requests.get(websiteRoot + link.attrib['href']).content)
                armamentContent = armamentPage.cssselect('#bodyContent')[0]
                pictures = getImages(armamentContent, numberOfImagesForSubItems)
            linkCounter += 1

        armamentFullName = createStringFromArray(0, linkWordsArray)
    else: #tries to get the name without the link if there are no links
        arrayofWordsIncludingX = getArrayOfWords(armamentString, "x", -1)
        armamentFullName = createStringFromArray(1, arrayofWordsIncludingX)

    quantity = parseIntFromStringArray(arrayOfWords, 0)


    charactersToRemove = ['(', ')']
    armamentFullTextWithout = removeOddCharacters(armamentString, charactersToRemove) #not necessarily the full name
    characterToSpace = ['/']
    armamentFullTextWithout = replaceOddCharacters(armamentFullTextWithout, characterToSpace, ' ')

    unitsToTry = ["mm", "cm", "kg"] #Prioritizes the first in the array
    armamentSize = 0
    armamentUnit = None
    for unit in unitsToTry:
        armamentSizeArray = getWordsBeforeUnit(armamentFullTextWithout, unit, 1)
        if len(armamentSizeArray) == 1:
            armamentSize = armamentSizeArray[0]
            armamentUnit = unit
            break #You want to prioritze the first unit
    if armamentUnit is not None:
        armament = Armament(armamentFullName, quantity, armamentUnit, armamentSize)
    else:
        armament = Armament(armamentFullName, quantity)
    if  armament.unknown:
        doNothing = None #currently do nothing
    elif armament.isCannon:
        calculateObjectsForType = armamentCalculateObjects["cannon"]
        #calculateObjectsForType["size"].addValue(armamentSize)
    elif armament.isMissile:
        armament #do nothing currently
    elif armament.isTorpedo: #Unit for torpedo guns and also deals with "calculate object"
        newUnit = "mm"
        newValue = conversionTable.convertUnit(armament.size, armament.unit, newUnit)
        armament.unit = newUnit
        armament.size = newValue
    else: #Unit conversion for normal guns and also deals with "calculate object"
        newUnit = "mm"
        newValue = conversionTable.convertUnit(armament.size, armament.unit, newUnit)
        armament.unit = newUnit
        armament.size = newValue

    armament = armament.toSerializableForm()
    armament['pictures'] = pictures #Should really be set in the armament constructor. Pictures defined at the top of the function and assigned under certain conditions in the link if statement

    return armament

def processArmor(armorElement, listTitleInput):
    """
    armorElement - the armor DOM element
    listTitleInput - relevant to armor in sublists
    """

    armor = None
    armorRange = False
    armorMinValue = None
    armorMaxValue = None
    armorUnit = None
    armorType = None
    listTitle = None

    armorFormattedText = formatString(replaceColonWithSpace((armorElement.text_content()))) #replace colon with space because some pages have errors where there is no space after the colon
    arrayOfWords = getArrayOfWords(armorFormattedText, None, 10)
    if len(arrayOfWords) >= 1:
        armorType = arrayOfWords[0]
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
                    if listTitleInput != None and len(armorElement.cssselect("a")) == 0: #you can identify a sub list item by its LACK of a link
                        armorType = listTitleInput + " " + armorType #previousArmorType is the title of the list such as "Deck" in "Deck": "First", "Second"

                    armor = Armor(armorType, armorMinValue, armorMaxValue, armorUnit, armorRange)

                    break #exit the unit for loop
        else:
            listTitle = armorType

    armorSerializable = None
    if armor != None:
        armorSerializable = armor.toSerializableForm()
        #print(armorSerializable)
    elif listTitle is not None:
        armorSerializable = {'listTitle': listTitle}
    return armorSerializable

def processClassAndType(valueString, ship):
    wordsArray = getArrayOfWords(valueString, None, -1)
    ship['class'] = wordsArray[0]

    ship['type'] = createStringFromArray(1, wordsArray) #All words after class are part of the type
def processStandardValue(valueString):
    """valueString -- Value string
        Looks for certain units. If the value contains a unit will return a dictionary with the unit and value keys.
        Else, it will just return the valueString
    """
    oddCharacters = ["(", ")"]
    replaceWithSpaceCharacters = ["[", "]", "/"]
    unitsToSearchFor = ["m", "km", "t", "long tons", "tons", "kW", "kn", "knots", "in", "inch"]

    returnValue = valueString #Will return the valueString if no units are found

    searchString = removeOddCharacters(valueString, oddCharacters) #Removes parentheses because some units are surrounded by them
    searchString = replaceOddCharacters(searchString, replaceWithSpaceCharacters, ' ')
    for unit in unitsToSearchFor:
        wordsBeforeUnit = getWordsBeforeUnit(searchString, unit, 1) #Returns an array of words before the unit of at most size 1. Note: units must be surrounded by spaces
        if len(wordsBeforeUnit) == 1: #If true, the string contains the unit
            returnValue = {
                "value": wordsBeforeUnit[0],
                "unit": unit
            }
            break
    return returnValue

def calculateComplement(valueString, ship):
    """
    valueString - The information string
    ship - The ship being modified

    THIS METHOD MIGHT BE CALLED MULTIPLE TIMES FOR ONE SHIP. IF it is, it will add the existing value with the new value.
    """
    currentComplementValue = 0
    if "complement" in ship:
        currentComplementValue = ship["complement"]
    wordsArray = getArrayOfWords(valueString, None, -1)
    for word in wordsArray:
        possibleNumber = isWordInt(word)
        if possibleNumber is not None:
            currentComplementValue += possibleNumber

    ship['complement'] = currentComplementValue

def processArmamentElements(armamentElements, configurationToKeep):
    valuesArray = []
    configurationCounter = -1 #If multiple configurations, the first one will have a date at the top of it
    armamentElementCounter = 0
    oneConfiguration = False #If there is only one configuration, keep all armaments. The counter increments the configuration counter by one when it runs into its first null (a date) because if there are two configurations, both have a dates. 1st configuration is after the FIRST null except for when there is only ONE configuration (no dates, no nulls)


    armamentCalculateObjects = {
    }
    typesOfArmament = ["normalGun", "torpedo", "cannon", "missile"]
    #Essentially creates two calculate objects per armament type
    for typeOfArmament in typesOfArmament:
        calculateDictionaryForType = {
            "size": Calculate([]),
            "quantity": Calculate([])
        }
        armamentCalculateObjects[typeOfArmament] = calculateDictionaryForType


    for arrayValueElement in armamentElements:
        armamentFormattedString = formatString(arrayValueElement.text_content())
        arrayOfWords = getArrayOfWords(armamentFormattedString, None, -1)
        isDate = len(arrayOfWords) < 2
        if isDate == False and armamentElementCounter == 0: #The first "value" is not a configuration year, so it must only have one configuration
            oneConfiguration = True
        if isDate:
            configurationCounter += 1
            if configurationCounter > configurationToKeep:
                break
        elif (configurationCounter == configurationToKeep) or (oneConfiguration):
            armament = processArmament(arrayValueElement, armamentFormattedString, arrayOfWords, armamentCalculateObjects)
            valuesArray.append(armament)
        armamentElementCounter += 1
    return valuesArray


def categorizeElement(key, value, valueElement, ship): #Will categorize elements that are not already in "arrays." For example, commissioned, decomissioned, recomissioned, ... are all listed as separate elements in the highest level of table
    #the key value is the key in the highest level of the info table aka under the info table: <key>:<some value>. Note: key has been converted to lowercase

    #Find the category that applies
    importantDateKeyWords = ['commission', 'launch', 'struck', 'laid', 'ordered']
    physicalAttributeKeyWord = ['draught', 'displacement', 'length', 'beam', 'depth of hold', 'tons burthen', 'speed', 'draft', 'range', 'installed power']

    physicalAttribute = False
    importantDate = False

    for keyWord in physicalAttributeKeyWord:
        if key.find(keyWord) >= 0:
            physicalAttribute = True
            break

    if physicalAttribute == False:
        for keyWord in importantDateKeyWords: #If else separate from for loop for organizational reasons rather. I didn't want a bunch of nested for loops and if statements
            if key.find(keyWord) >= 0:
                importantDate = True
                break

    #Add element to category. Perform necessary operations
    if physicalAttribute:
        ship["physicalAttributes"][key] = processStandardValue(value) #ship["physicalAttributes"] object defined at ship construction
    elif importantDate:
        date = createDateObject(value).toSerializableForm()
        if date is not None:
            dateElement = {"significance": key, "date": date}
            ship['importantDates'].append(dateElement)
    elif key.find('awards') >= 0: #Some pages have this as a list. Some only have it as a single element. Standardizes to an array
        ship['awards'].append(value)
    elif key.find('class') >=0: #Separates class and type in a cell element. First word is always class. Words after are always type. Some ships only have a "type" not a class. This statement won't evluate in that situation, so it still works.
        processClassAndType(value, ship)
    elif key == "armor" or key == "armour":
        #There's only a single unit of armor AKA there must be none because the key is "armor" meaning there is no type key
        ship["armor"] = []
    elif key == "armament":
        #There's only one gun
        valuesArray = processArmamentElements([valueElement], 0)
        ship["armament"] = valuesArray
    elif key == "complement":
        calculateComplement(value, ship)
    else:   #Catch all
        ship[key] = processStandardValue(value)

def processRow(rowElement, shipBeingUpdated):
    cellElements = rowElement.cssselect("td")
    if len(cellElements) == 2 and len(cellElements[1].cssselect('img')) == 0: #Ensure it actually has a value and the value does not have a nimage
        key = formatString(cellElements[0].text_content()).lower() #format string and convert it to lower case
        valueElement = cellElements[1]
        arrayValueElements = valueElement.cssselect("ul>li")
        if len(arrayValueElements)==0: #dealing with a single value element aka not an array
            categorizeElement(key, formatString(valueElement.text_content()), valueElement, ship) # the object referenced by 'ship' modified in function. thus, no ship returned because reference points to the same object
        else :
            keysWithNoArray = ["draught", "length", "displacement"] #Should contain the keys that should NOT have an array of objects. For example, some ships have multiple displacements listed--scraper should only keep one

            valuesArray = []
            addValuesArrayToShip = True
            if key == "armament":
                configuration = int(shipBeingUpdated['configuration']) #Which configuration do you want if their are multiple configurations
                valuesArray = processArmamentElements(arrayValueElements, configuration) #deals with processing armament elements
            elif key == "armor":
                lastListTitle = None
                for armorElement in arrayValueElements:
                    armor = processArmor(armorElement, lastListTitle)
                    if armor != None and 'listTitle' in armor:
                        lastListTitle = armor["listTitle"]
                    elif armor != None:
                        valuesArray.append(armor)

            elif key == "installed power": #Some ships just have the installed power value listed. Some have a list of items under installed power including the value, boilers, ... This will just keep the actual value
                for powerElement in arrayValueElements:
                    value = formatString(powerElement.text_content())
                    processedValue = processStandardValue(value)
                    if processedValue != value: #a dictionary was returned meaning it found a unit (kW)
                        ship[key] = processedValue
                        addValuesArrayToShip = False
                        break #exits the for loop
            elif key == "complement":
                for complementElement in arrayValueElements:
                    valueString = formatString(complementElement.text_content())
                    categorizeElement(key, valueString, complementElement, ship) #See how categorize elemtn categorizes complement. It will sum the values of all complement elements
                addValuesArrayToShip = False
            else:
                #If the property should not have an array of objects, it will only save the LAST value not an array of values
                for noArrayKey in keysWithNoArray: #keysWithNoArray defined at top
                    if key == noArrayKey:
                        lastValueElement = arrayValueElements[len(arrayValueElements) - 1] #Will only save the last value
                        categorizeElement(key, formatString(lastValueElement.text_content()), lastValueElement, ship)
                        addValuesArrayToShip = False
                        break

                if addValuesArrayToShip:
                    for arrayValueElement in arrayValueElements:
                        value = processStandardValue(formatString(arrayValueElement.text_content()))
                        valuesArray.append(value)

            if key.lower().find("awards") >= 0: #Sometimes awards are listed as a list. Sometimes they are just a single value. categorizeElement makes the awards key "awards". This converts "honors and awards" to "awards" as the key
                key = "awards"

            if addValuesArrayToShip:
                shipBeingUpdated[key] = valuesArray
    return shipBeingUpdated


#Main script
global numberOfImagesForSubItems
global maxNumberOfImagesForAShip

#GET SETTINGS


settingsPath = "./shipSettings.json"
inputPath = "./shipsToScrape.json"

with open(settingsPath, 'r') as file:
    ingestSettings = json.load(file)

with open(inputPath, 'r') as file:
    shipsInput = json.load(file)


shipPages = shipsInput

websiteRoot = ingestSettings["websiteRoot"]

maxNumberOfImagesForAShip = ingestSettings["maxNumberOfImagesForAShip"]
numberOfImagesForSubItems = ingestSettings["numberOfImagesForSubsItems"]


# BEGINS SCRAPING
conversionTable = UnitConversionTable()
shipIDCounter = 0
ships = []

for page in shipPages:
    #Parrellize ?
    #BINARY SEARCH TREES FOR COMMON ATTRIBUTES

    webpage = requests.get(page['url'])
    tree = html.fromstring(webpage.content)
    infoBox = tree.cssselect(".infobox")[0]
    content = tree.cssselect("#bodyContent")[0]
    textContent = content.cssselect("#mw-content-text")[0]
    firstParagraph = textContent.cssselect("p")[0]
    description = formatString(firstParagraph.text_content())
    oddCharactersInDescription = ["[a]"]
    description = removeOddCharacters(description, oddCharactersInDescription)
    #Scrapes ship name
    shipName = tree.cssselect("#firstHeading")[0].text_content()
    ship = {'ID': shipIDCounter,
            'scrapeURL': page['url'], #used to check uniqueness of ship AKA has it already been added. Note: I could check name and date (some ships have the same name), but I only need to do 1 comparison with URL
            'configuration': page['configuration'],
            'importantDates': [],
            'awards': [],
            'armament': [],
            'armor': [],
            'description': description,
            'physicalAttributes': {}
            }
    shipImages = []

    #Scrapes all images and descriptions
    mainPicture = getInfoBoxPicture(infoBox) #Gets the main picture in the infobox
    textPictures = getImages(textContent, maxNumberOfImagesForAShip - 1) #-1 because of the main picture
    ship["pictures"] = [mainPicture] + textPictures

    #get most ship infoBox
    rows = infoBox.cssselect("tr")
    for row in rows:
        processRow(row, ship)


    #print (infoBox.text_content())


    #Appends the ship to the list of ships
    ships.append(ship)
    shipIDCounter+=1
print(json.dumps(ships))
