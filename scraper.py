import os
import sys
from lxml import cssselect
from Armament import Armament
from Armor import Armor
from lxml import html
from Date import Date
ship_scraping_path = os.environ.get('SHIP_SCRAPER') # check environment variable. if not set, use a default value
if ship_scraping_path is None:
    ship_scraping_path = "A:\DevenirProjects"
else:
    ship_scraping_path += '/..'
sys.path.insert(0, ship_scraping_path)
import Config
from UnitConversionTable import UnitConversionTable
from Calculate import Calculate
from ABoatDatabase import BoatDatabase
from unidecode import unidecode
import requests
import sys
from sys import exit
import traceback
import json
from ship_compare.compare_ship_to_database import DatabaseCompare
from ship_compare.ship_network_algo.run_algos_on_network import run_algos
from utilities.get_environment import CONFIG_PATH
from utilities.get_environment import RECOMMENDED_UNITS



#Global variables
global websiteRoot #Assigned in the settings area of the script
global conversionTable #ConversionTable

def error (message) :
    print("ERROR: " + message)

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
        oddCharacters = [","] # Some people use commas to format large numbers
        word = removeOddCharacters(word, oddCharacters)
        intObject = int(word)
    except:
        #traceback.print_exc()
        intObject = None
    return intObject
def isWordFloat(word):
    """
    word - Word being observed
    If: the word is an int, the int will be returned
    Else: nothing will be returned
    """
    try:
        oddCharacters = [","] # Some people use commas to format large numbers
        word = removeOddCharacters(word, oddCharacters)
        value = float(word)
    except:
        #traceback.print_exc()
        value = None
    return value

def process_range (range_string):
    """
    rangeString -- should ONLY be the range string (no spaces or other words)
    will return None if not a range
    will return Average if range
    """
    possible_number = None
    rangeIndex = range_string.find("-")
    if rangeIndex > 0: # if a dash exists to represent a range of numbers, it would make no sense to be at the first character in the string so > 0 (or it might not even be in the string)
        firstValue = isWordFloat(range_string[0:rangeIndex])
        secondValue = isWordFloat(range_string[rangeIndex + 1:])
        #print("First value, %s, and second value, %s."%(firstValue, secondValue))
        if firstValue is not None and secondValue is not None: # If it is a range, find the average. Treat that like the complement number
            averageObject = Calculate([firstValue, secondValue])
            possible_number = averageObject.calculateAverage()
    return possible_number

def parseIntFromStringArray(haystackArray, intToKeep):
    intCounter = -1
    """
    intToKeep -- 0: first int 1: second int
    Will return None if no int found
    """
    intObject = None
    for word in haystackArray:
        possibleInteger = isWordFloat(word)
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

def getValueFromUnitString (string, unit):
    """Tries to pull a value from a string in the following format: '{value}{unit}'. Note there is no space between the two. Else returns none"""
    value = None;
    sizeOfString = len(string)
    sizeOfUnit = len(unit)
    indexOfUnit = string.find(unit);
    if indexOfUnit > 0 and indexOfUnit + sizeOfUnit == sizeOfString: # There must be room for a value with at least 1 digit so the unit can't be at index 0 and there can't be anything after the unit
        valueString = string[0:indexOfUnit] # Everything before the value must be part of the value
        value = isWordFloat(valueString) # Will return None if not int . Change to double?

    #print("String: " + string + " Unit: " + unit + " Value: ", value)
    return value


def deleteAnnotations(string):
    """deletes in-line annotations found on pages. For example, "[1]"""
    stringBeingChecked = string
    formattedString = ""

    openBracket = stringBeingChecked.find("[")
    closeBracket = stringBeingChecked.find("]")
    while openBracket >= 0 and closeBracket >= 0:
        if openBracket + 2 == closeBracket: #traditional annotation
            formattedString = formattedString + stringBeingChecked[0:openBracket]
            stringBeingChecked = stringBeingChecked[closeBracket + 1:]

        elif closeBracket > openBracket: #crop the string to relevant areas. the brackets found were not in normal annotation format
            formattedString = formattedString + stringBeingChecked[0:closeBracket + 1]
            stringBeingChecked = stringBeingChecked[closeBracket + 1:]
        else: #crop the string to relevant areas. the brackets found were not in normal annotation format
            formattedString = formattedString + stringBeingChecked[0:openBracket + 1]
            stringBeingChecked = stringBeingChecked[openBracket + 1:]

        #Update variables for loop
        openBracket = stringBeingChecked.find("[")
        closeBracket = stringBeingChecked.find("]")
    #when the loop exists there are no more brackets, so the "stringBeingChecked" must be formatted
    formattedString = formattedString + stringBeingChecked
    return formattedString

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
def formatShipName(shipName):
    """Formats a ship name if one is not provided in the scraper parameters"""
    wordsToFilter = ["hms", "uss", "battleship", "german", "french", "japanese", "italian", "american", "ijn", "(", "sms", "cruiser"] #in lower case. shipName will be converted to lower case for comparison

    shipWords = getArrayOfWords(shipName, None, -1)
    if len(shipWords) > 1: #Some ship names might be more than one word. This just filters out the names that are already fine
        counter = 0
        while counter < len(shipWords):
            word = shipWords[counter]

            removeWord = False


            for filterWord in wordsToFilter:
                word = word.lower()
                if word.find(filterWord) >= 0:
                    removeWord = True
                    break
            if removeWord:
                shipWords.pop(counter) #Don't increment counter because everything has been shifted down one
            else:
                counter += 1

        shipName = createStringFromArray(0, shipWords)
    return shipName


def getInfoBoxPicture(boxWithPicture):
    """returns picture object"""
    pictureObject = None;

    images = boxWithPicture.cssselect("img")
    if len(images) > 0:
        picture = images[0]
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
                error("A date object could not be created from the string: " + dateString)
                dateObject = None

    return dateObject

def processArmament(armamentElement, armamentString, arrayOfWords, armamentTypeObjects): # Should probably transfer ALL of this code to the Armament class
    """
    armamentElement - the armament dom element
    armamentString and arrayOfWords - Array of words from armament. Sent as parameter because it is already "calcualted" when checking to see if the armament is a date
    armamentTypeObject - A dictionary with a Calculate(.py) object for each type of armament. Used to calculate average, median, and related values for size and quantity. See processArmamentElements
    """
    pictures = []
    armament = None
    armamentLinks = armamentElement.cssselect('a')


    if len(armamentLinks) > 0:#Assumes the full name is contained within links if evaluates to true
        linkWordsArray = [] #each 'word' is probably a phrase
        linkCounter = 0
        mostRecentPageTitle = None
        for link in armamentLinks:
            linkWordsArray.append(formatString(link.text_content()))
            #Gets imagesS for armament. Uses the last armament link if there are more than one.
            if linkCounter == len(armamentLinks) - 1:
                armamentPage = html.fromstring(requests.get(websiteRoot + link.attrib['href']).content)
                armamentContent = armamentPage.cssselect('#bodyContent')[0]
                mostRecentPageTitle = armamentPage.cssselect("#firstHeading")[0].text_content() # Gets the page title
                infoBoxes =  armamentPage.cssselect(".infobox")
                if len(infoBoxes) > 0: # Gets the main picture
                    mainPictureBox = infoBoxes[0]
                    primaryPicture = getInfoBoxPicture(mainPictureBox)
                    if primaryPicture is not None:
                        pictures.append(primaryPicture)
                pictures += getImages(armamentContent, numberOfImagesForSubItems)

            linkCounter += 1
        # armamentFullName = createStringFromArray(0, linkWordsArray) . Links tended to only include part of the name. More efficient but less accurate

    # tries to get the name without the link if there are no links
    arrayOfName = getArrayOfWords(armamentString, "x", -1)
    #print("ARMAMENT: ", arrayOfName, " FULL", armamentString)
    # Gets quantity info
    quantityBeforeConversion = parseIntFromStringArray(arrayOfWords, 0)
    quantity = conversionTable.convertUnit(quantityBeforeConversion, "word", arrayOfName[1]) # If double, triple are the first words, will multiply the quantity by the appropriate multiplier. If it's some other word (or number), it will just return the original value
    if quantityBeforeConversion != quantity: # One of the special "quantity" words must be the first word. Remove the word from the namebecause we converted the quantity to match the word aka 3 triple = 9 barrels
        arrayOfName.pop(0) # removes the first word.

    # Get name from array of words after x. The first word might have been removed depending on the conversion
    armamentFullName = createStringFromArray(1, arrayOfName)


    if quantity is None:# Should only be called if an error occurs. For example: New York and torpedo tubes
        error_string = "Source: " + arrayOfWords + "\nName: " +armamentFullName, "with quantity", quantity
        error(error_string)
        armament = None;
    else:
        charactersToRemove = ['(', ')']
        armamentFullTextWithout = removeOddCharacters(armamentString, charactersToRemove) #not necessarily the full name
        characterToSpace = ['/']
        armamentFullTextWithout = replaceOddCharacters(armamentFullTextWithout, characterToSpace, ' ')

        unitsToTry = ["mm", "cm", "kg", "in", "inch"] #Prioritizes the first in the array
        armamentSize = 0
        armamentUnit = None
        for unit in unitsToTry:
            armamentSizeArray = getWordsBeforeUnit(armamentFullTextWithout, unit, 1)

            if len(armamentSizeArray) == 1:
                armamentSize = armamentSizeArray[0]
                armamentUnit = unit
                break #You want to prioritze the first unit

        if armamentUnit is None: # Try to find the unit assuming there is no space between the value and unit (not used by default because resource intensive)
            for word in arrayOfWords:
                for unit in unitsToTry:
                    armamentSize = getValueFromUnitString(word, unit)
                    if armamentSize is not None:
                        armamentUnit = unit;
                        break
                if armamentUnit is not None: # An armament unit was found
                    break

        if armamentUnit is not None:
            armament = Armament(armamentFullName, quantity, armamentUnit, armamentSize)
        elif quantity is not None:
            armament = Armament(armamentFullName, quantity)

        armament = armament.toSerializableForm()
        armament['pictures'] = pictures #Should really be set in the armament constructor. Pictures defined at the top of the function and assigned under certain conditions in the link if statement

        #Armament is now a dictionary not an object
        if  armament["unknown"]:
            doNothing = None #currently do nothing. unknown armaments are not added
        elif armament["isCannon"]:
            #After unit conversions
            calculateObjectsForType = armamentTypeObjects["cannon"]
            calculateObjectsForType["sizeCalculate"].addValueWithQuantity(armament["size"], armament["quantity"])
            calculateObjectsForType["armaments"].append(armament)    #Add it to it's appropriate category


        elif armament["isMissile"]:
            #After unit conversions
            calculateObjectsForType = armamentTypeObjects["missile"]
            calculateObjectsForType["sizeCalculate"].addValueWithQuantity(armament["size"], armament["quantity"])
            calculateObjectsForType["armaments"].append(armament)    #Add it to it's appropriate category

        elif armament["isTorpedo"]: #Unit for torpedo guns and also deals with "calculate object"
            newUnit = "mm"
            newValue = conversionTable.convertUnit(armament["size"], armament["unit"], newUnit)
            armament["unit"] = newUnit
            armament["size"] = newValue

            #After unit conversions
            calculateObjectsForType = armamentTypeObjects["torpedo"]
            calculateObjectsForType["sizeCalculate"].addValueWithQuantity(armament["size"], armament["quantity"])

            calculateObjectsForType["armaments"].append(armament)    #Add it to it's appropriate category


        else: #Unit conversion for normal guns and also deals with "calculate object"
            newUnit = "mm"
            newValue = conversionTable.convertUnit(armament["size"], armament["unit"], newUnit)
            armament["unit"] = newUnit
            armament["size"] = newValue

            #After unit conversions
            calculateObjectsForType = armamentTypeObjects["normalGun"]
            calculateObjectsForType["sizeCalculate"].addValueWithQuantity(armament["size"], armament["quantity"])

            calculateObjectsForType["armaments"].append(armament)    #Add it to it's appropriate category

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
    armorFormattedText = deleteAnnotations(armorFormattedText)

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
                        armorMaxValue = isWordFloat(armorWidthArray[0]) #0 is the first word before the unit
                        armorMinValue = isWordFloat(armorWidthArray[2]) #2 is the third word after the unit
                    elif armorWidthArray[0].find("-") >= 0:
                        armorRange = True
                        armorRangeValues = armorWidthArray[0] #The armor is a range. The first word before the unit has a dash in it (presumbably A-B where A and B are some constant)
                        dashIndex = armorRangeValues.find("-")
                        armorMinValue = isWordFloat(armorRangeValues[0:dashIndex])
                        armorMaxValue = isWordFloat(armorRangeValues[dashIndex + 1:])
                    else: #Not a range of values
                        armorMinValue = isWordFloat(armorWidthArray[0])
                        armorMaxValue = armorMinValue

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
    valueString = valueString.lower()
    indexOfClass = valueString.find("class")
    if indexOfClass == -1:
        print("Could not find type and class for " + ship["displayName"] + ". Trying basic method...")
        wordsArray = getArrayOfWords(valueString, None, -1)
        classOfShip = wordsArray[0]
        type = createStringFromArray(1, wordsArray) #All words after class are part of the type
    else:
        endOfClassWord = indexOfClass + 5
        classOfShip = valueString[0:endOfClassWord]
        type = valueString[endOfClassWord:]

    ship["class"] = classOfShip
    ship["type"] = type

def processStandardValue(valueString):
    """valueString -- Value string
        Looks for certain units. If the value contains a unit will return a dictionary with the unit and value keys.
        Else, it will just return the valueString
    """
    # print(valueString)
    valueString = valueString.lower(); # Make the string lowercase

    returnValue = valueString # Will return the valueString if no units are found

    oddCharacters = ["(", ")"]
    replaceWithSpaceCharacters = ["[", "]"]
    unitsToSearchFor = ["km", "nmi", "miles", "kn", "knots", "m", "meters", "ft", "feet", "t", "long tons", "tons", "kw", "in", "inch"] # Range units prioritized first because some ranges have speeds associated with them (we don't want to pull the speed value)


    searchString = removeOddCharacters(valueString, oddCharacters) #Removes parentheses because some units are surrounded by them
    searchString = replaceOddCharacters(searchString, replaceWithSpaceCharacters, ' ')
    for unit in unitsToSearchFor:
        wordsBeforeUnit = getWordsBeforeUnit(searchString, unit, 1) #Returns an array of words before the unit of at most size 1. Note: units must be surrounded by spaces
        if len(wordsBeforeUnit) == 1: # If true, the string contains the unit
            value_word = wordsBeforeUnit[0]
            value = isWordFloat(value_word)
            if value is None: # if it can't be processed as a float
                # maybe it's a range?
                value = process_range(value_word)
                if value is None: # fallback, don't try to pull out a number.
                    error("Could not process value %s from %s"%(value_word, valueString))
                    value = value_word
            returnValue = {
                "value": value,
                "unit": unit
            }
            # print(returnValue)
            break
    return returnValue

def calculateComplement(valueString, ship):
    """
    valueString - The information string
    ship - The ship being modified

    THIS METHOD MIGHT BE CALLED MULTIPLE TIMES FOR ONE SHIP. IF it is, it will add the existing value with the new value.
    """
    valueString = deleteAnnotations(valueString)
    currentComplementValue = 0
    valueStringContainsOfficersAndEnlisted = valueString.find("officers") > 0 and valueString.find("enlisted") > 0 # IF true, the any other "complement" strings must just be from a different configuration, so only keep the value from the latest complement string(don't sum all values).
    if "complement" in ship:
        currentComplementValue = ship["complement"]
    if currentComplementValue == 0 or not valueStringContainsOfficersAndEnlisted: # SEE ABOVE. Function calculateCOmplement might be called multiple times if multiple configurations or complement listed as series of strings. If multiple configurations, keep the first
        wordsArray = getArrayOfWords(valueString, None, -1)
        for word in wordsArray:
            possibleNumber = process_range(word) # maybe it's a range
            if possibleNumber is None: # if it is not a range, maybe it's a normal number
                possibleNumber = isWordInt(word)
                if possibleNumber is not None:
                    currentComplementValue += possibleNumber
            else:
                currentComplementValue += possibleNumber

        ship['complement'] = currentComplementValue

def convert_value_object (key, value_object):
    """converts to the recommended unit or default unit (depending on what is configured)"""
    # convert physical attribute to the preferred unit for the physical attribute
    if key in RECOMMENDED_UNITS: # if a unit exists for the physical attribute (key should be the name version of the physical attribute (speed, beam...))
        preferred_unit = RECOMMENDED_UNITS[key]
        converted_value = conversionTable.convertUnit(value_object["value"], value_object["unit"], preferred_unit)
        if converted_value is not None: # presumably this if statement is unnecessary. If configured correctly, the recommended unit DEFINITELY should be in the conversion dictioanry
            value_object["value"] = converted_value
            value_object["unit"] = preferred_unit
        else:
            error("Converting %s to %s failed"%(value_object["unit"], preferred_unit))
    else:
        error("A recommended unit could not be found for physical attribute %s"%(key))
    return value_object


def processArmamentElements(armamentElements, configurationToKeep):
    values = []
    armamentElementCounter = 0
    oneConfiguration = False #If there is only one configuration, keep all armaments. The counter increments the configuration counter by one when it runs into its first null (a date) because if there are two configurations, both have a dates. 1st configuration is after the FIRST null except for when there is only ONE configuration (no dates, no nulls)

    #4 keys. All 4 types of armaments. Each key stores an array of armaments and its calculate object
    armamentTypeObjects = {
    }

    typesOfArmament = ["normalGun", "torpedo", "cannon", "missile"]

    #Essentially creates one calculate objects per armament type. Sent as a parameter to processArmament
    for typeOfArmament in typesOfArmament:
        calculateDictionaryForType = {
            "sizeCalculate": Calculate([]),
            "armaments": []
        }
        armamentTypeObjects[typeOfArmament] = calculateDictionaryForType

    configurationCounter = -1 #If multiple configurations, the first one will have a date at the top of it

    for arrayValueElement in armamentElements:
        armamentFormattedString = formatString(arrayValueElement.text_content())
        arrayOfWords = getArrayOfWords(armamentFormattedString, None, -1)
        isDate = len(arrayOfWords) <= 3
        if isDate == False and armamentElementCounter == 0: #The first "value" is not a configuration year, so it must only have one configuration
            oneConfiguration = True
        if isDate:
            configurationCounter += 1
            if configurationCounter > configurationToKeep or len(values) > 0: # Stop adding armaments if you've encountered another date past your configuration OR you've added armaments and have encountered a date
                # if values.length> 0 - probably means was scraping first configuration (0th) and the first configuration did not have a "date header"
                break
        elif (configurationCounter == configurationToKeep) or (oneConfiguration):
            if armamentFormattedString.find("removed") == -1: # Some times armaments are listed when they are removed. Ensures the armament wasn't removed
                armament = processArmament(arrayValueElement, armamentFormattedString, arrayOfWords, armamentTypeObjects)
                if armament is not None:
                    values.append(armament)
                else:
                    print("Tried to add a None armament for: ", arrayOfWords)
        armamentElementCounter += 1

    #Get a serializable dictionary that contains each armament type's Calculate Object in the form of a dictionary
    for armamentType in typesOfArmament:
        armamentTypeObject = armamentTypeObjects[armamentType]
        armamentTypeObject["sizeCalculate"] = armamentTypeObject["sizeCalculate"].calculationsDictionary() #Serializes the calculate object for size
        armamentTypeObject["armaments"] = armamentTypeObject["armaments"]


    return armamentTypeObjects



def categorizeElement(key, value, valueElement, ship): #Will categorize elements that are not already in "arrays." For example, commissioned, decomissioned, recomissioned, ... are all listed as separate elements in the highest level of table
    #the key value is the key in the highest level of the info table aka under the info table: <key>:<some value>. Note: key has been converted to lowercase

    #Find the category that applies
    importantDateKeyWords = ['commission', 'launch', 'struck', 'laid', 'ordered', 'complete']
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
        valueObject = processStandardValue(value)
        valueObject = convert_value_object(key, valueObject)

        ship["physicalAttributes"][key] = valueObject #ship["physicalAttributes"] object defined at ship construction
    elif importantDate:
        date = createDateObject(value)
        if date is not None:
            date = createDateObject(value).toSerializableForm()
            ship['importantDates'][key] = date # Essentially a hash map to make searching faster
    elif key.find('awards') >= 0: #Some pages have this as a list. Some only have it as a single element. Standardizes to an array
        ship['awards'].append(value)
    elif key.find('class') >=0: #Separates class and type in a cell element. First word is always class. Words after are always type. Some ships only have a "type" not a class. This statement won't evluate in that situation, so it still works.
        processClassAndType(value, ship)
    elif key == "armor" or key == "armour":
        #There's only a single unit of armor AKA there must be none because the key is "armor" meaning there is no type key
        ship["armor"] = {"armorObjects": [],
                         "calculations": {}
                        }
    elif key == "armament":
        #There's only one gun
        values = processArmamentElements([valueElement], 0)
        ship["armament"] = values
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
            keysWithNoArray = ["draught", "length", "displacement", "speed"] #Should contain the keys that should NOT have an array of objects. For example, some ships have multiple displacements listed--scraper should only keep one

            values = []
            addvaluesToShip = True
            if key == "armament":
                configuration = int(shipBeingUpdated['configuration']) #Which configuration do you want if their are multiple configurations
                values = processArmamentElements(arrayValueElements, configuration) #deals with processing armament elements
            elif key == "armor" or key == "armour":
                key = "armor" #Change key if it's "armour"
                values = {"armorObjects": [],
                         "calculations": {}
                }
                lastListTitle = None
                armorCalculateObject = Calculate([])
                for armorElement in arrayValueElements:
                    armor = processArmor(armorElement, lastListTitle)
                    if armor != None and 'listTitle' in armor:
                        lastListTitle = armor["listTitle"]
                    elif armor != None:
                        values["armorObjects"].append(armor)

                        #Add armor width to Calculate object. NOTE: This does not account for weights (weighted values) of armor AKA if 5 mm exists at only 1% of the ship, it is treated the same as 1000mm of armor that exists for 99% of the ship.
                        armorCalculateObject.addValue(armor["minValue"])
                        if(armor["range"]):
                            armorCalculateObject.addValue(armor["maxValue"])
                values["calculations"] = armorCalculateObject.calculationsDictionary()


            elif key == "installed power": #Some ships just have the installed power value listed. Some have a list of items under installed power including the value, boilers, ... This will just keep the actual value
                for powerElement in arrayValueElements:
                    value = formatString(powerElement.text_content())
                    processedValue = processStandardValue(value)
                    if processedValue != value: #a dictionary was returned meaning it found a unit (kW)
                        ship[key] = processedValue
                        addvaluesToShip = False
                        break #exits the for loop
            elif key == "complement":
                for complementElement in arrayValueElements:
                    valueString = formatString(complementElement.text_content())
                    categorizeElement(key, valueString, complementElement, ship) #See how categorize elemtn categorizes complement. It will sum the values of all complement elements
                addvaluesToShip = False
            else:
                #If the property should NOT have an array of objects, it will only save the LAST value not an array of values
                for noArrayKey in keysWithNoArray: #keysWithNoArray defined at top
                    if key == noArrayKey:
                        lastValueElement = arrayValueElements[len(arrayValueElements) - 1] #Will only save the last value
                        categorizeElement(key, formatString(lastValueElement.text_content()), lastValueElement, ship)
                        addvaluesToShip = False
                        break

                if addvaluesToShip:
                    for arrayValueElement in arrayValueElements:
                        value = processStandardValue(formatString(arrayValueElement.text_content()))
                        values.append(value)

            if key.lower().find("awards") >= 0: #Sometimes awards are listed as a list. Sometimes they are just a single value. categorizeElement makes the awards key "awards". This converts "honors and awards" to "awards" as the key
                key = "awards"

            if addvaluesToShip:
                shipBeingUpdated[key] = values
    return shipBeingUpdated


#Main script
global numberOfImagesForSubItems
global maxNumberOfImagesForAShip
runScript = True

#GET SETTINGS through parameters passed to script
try:
    if len(sys.argv) == 1: #the script name is always the first argument
        print("No arguments were passed, so the script will not run.")
        print("Please pass: {settingsPath} {ingestPath} or {ingestJSON}")
        runScript = False
    else:
        if len(sys.argv) == 2: #Use default settings because JSON is being directly passed. Not JSONfile path. See help message at bottom
            settingsPath = CONFIG_PATH #use default settings
            shipsJSON = sys.argv[1]
            shipsInput = json.loads(shipsJSON) #windows shell removes quotes before sending argument, so sending JSON through windows does not work.
        else:
            settingsPath = sys.argv[1] #get settings path
            with open(sys.argv[2], 'r') as file: #get ships to ingest
                shipsInput = json.load(file)

        ingestSettings = Config.getConfigFromPath(settingsPath)
except Exception as exception:
    print("An error occurred with the parameter(s) you entered, so the script will not be run")
    print("Please pass: {settingsPath} {ingestPath} or {ingestJSON}")
    print(exception) #Print exception because when running child process from node, only output directly printed to console can be seen
    traceback.print_exc()
    runScript = False



if runScript: #runScript is set false if one of the parameters is bad
    shipPages = shipsInput

    websiteRoot = ingestSettings["websiteRoot"]
    databaseIp = ingestSettings["dbIp"]
    databasePort = int(ingestSettings["dbPort"])
    maxNumberOfImagesForAShip = ingestSettings["maxNumberOfImagesForAShip"]
    numberOfImagesForSubItems = ingestSettings["numberOfImagesForSubsItems"]


    # BEGINS SCRAPING
    boatDatabase = BoatDatabase(databaseIp, databasePort)
    conversionTable = UnitConversionTable()
    shipCounter = 0
    ships = []

    for page in shipPages:
        #Parrellize ?
        #BINARY SEARCH TREES FOR COMMON ATTRIBUTES

        webpage = requests.get(page['url'])
        tree = html.fromstring(webpage.content)
        infoBox = tree.cssselect(".infobox")[0]
        content = tree.cssselect("#bodyContent")[0]
        textContent = tree.cssselect("#mw-content-text")[0]
        firstParagraph = content.cssselect(".mw-parser-output > p")[0]
        description = formatString(firstParagraph.text_content())
        oddCharactersInDescription = ["[a]"]
        description = removeOddCharacters(description, oddCharactersInDescription)
        #Scrapes ship name
        shipName = tree.cssselect("#firstHeading")[0].text_content()

        if 'displayName' not in page: #displayName is the name that will be displayed on the website. a display name was not provided
            displayName = formatShipName(shipName)
        else:
            displayName = page['displayName']

        ship = {
                'scrapeURL': page['url'], #used to check uniqueness of ship AKA has it already been added. Note: I could check name and date (some ships have the same name), but I only need to do 1 comparison with URL
                'configuration': page['configuration'],
                'displayName': displayName,
                'name': shipName,
                'importantDates': {},
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

        # All Information Scraped. Save information

        # Save to MongoDatabase
        boatDatabase.protectedInsertShip(ship)
        #print notify
        print("----SCRAPER COMPLETE----")
        print("Calculating edges and relatedness...")

        # Generate edges
        databaseCompare = DatabaseCompare(ship)
        #print(databaseCompare.getSerializableEdgesBetweenShips())
        databaseCompare.writeEdgesToDatabase()
        databaseCompare.closeDatabases()


        # Appends the ship to the list of ships
        ships.append(ship)
        # Increment ship counter
        shipCounter+=1
    # After all the edges have been drawn between the ships, calculate the shortest paths
    run_algos()
    exit(0)
    print(json.dumps(ships))
