from lxml import cssselect
from Armament import Armament
from Armor import Armor
from lxml import html
from Date import Date
from unidecode import unidecode
import requests
import sys
import traceback
import json

#Global variables
global websiteRoot #Assigned in the settings area of the script


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
def parseIntFromStringArray(haystackArray, intToKeep):
    intCounter = -1
    """
    intToKeep -- 0: first int 1: second int
    Will return None if no int found
    """
    intObject = None
    for word in haystackArray:
        try:
            intObject = int(word)
            intCounter += 1
            if intCounter == intToKeep:
                break
        except:
            #traceback.print_exc()
            intObject = None
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
            image = imageWrapper.cssselect("img")[0] #Actual image object
            caption = imageWrapper.cssselect(".thumbcaption")[0] #Holds the description

            imageObject = {}
            src = image.attrib["src"][2:] #remove the first two characters of the URL because they are a filepaths for the server ('//'), not URL. Represent root.
            description = formatString(caption.text_content())
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

def processArmament(armamentElement):
    pictures = []
    armamentString = formatString(armamentElement.text_content())
    armament = None
    arrayOfWords = getArrayOfWords(armamentString, None, -1)
    if(len(arrayOfWords) > 1): #if it equals 1, then it's a date (extraneous, not armament, date of gun configuration)
        armamentLinks = armamentElement.cssselect('a')
        armamentLink = None


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
        armament = Armament(armamentFullName, quantity)


        charactersToRemove = ['(', ')']
        armamentFullTextWithout = removeOddCharacters(armamentString, charactersToRemove) #not necessarily the full name
        unitsToTry = ["mm", "cm", "pounder"] #Prioritizes the first in the array
        for unit in unitsToTry:
            armamentSizeArray = getWordsBeforeUnit(armamentFullTextWithout, unit, 1)
            if len(armamentSizeArray) == 1:
                armament.size = armamentSizeArray[0]
                armament.unit = unit
                break #You want to prioritze the first unit
        armament = armament.toSerializableForm()
        armament['pictures'] = pictures #Should really be set in the armament constructor. Pictures defined at the top of the function and assigned under certain conditions in the link if statement

    return armament

def processArmor(armorElement, listTitleInput):

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
    unitsToSearchFor = ["m", "km", "t", "long tons", "tons", "kW", "kn", "knots"]

    returnValue = valueString #Will return the valueString if no units are found

    searchString = removeOddCharacters(valueString, oddCharacters) #Removes parentheses because some units are surrounded by them
    for unit in unitsToSearchFor:
        wordsBeforeUnit = getWordsBeforeUnit(searchString, unit, 1) #Returns an array of words before the unit of at most size 1. Note: units must be surrounded by spaces
        if len(wordsBeforeUnit) == 1: #If true, the string contains the unit
            returnValue = {
                "value": wordsBeforeUnit[0],
                "unit": unit
            }
            break
    return returnValue

def categorizeElement(key, value, valueElement, ship): #Will categorize elements that are not already in "arrays." For example, commissioned, decomissioned, recomissioned, ... are all listed as separate elements in the highest level of table
    #the key value is the key in the highest level of the info table aka under the info table: <key>:<some value>. Note: key has been converted to lowercase

    #Find the category that applies
    importantDateKeyWords = ['commission', 'launch', 'struck', 'laid', 'ordered']

    importantDate = False
    for keyWord in importantDateKeyWords: #If else separate from for loop for organizational reasons rather. I didn't want a bunch of nested for loops and if statements
        if key.find(keyWord) >= 0:
            importantDate = True
            break

    #Add element to category. Perform necessary operations
    if importantDate:
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
        ship["armament"].append(processArmament(valueElement))
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
            valuesArray = []
            addValuesArrayToShip = True
            if key == "armament":
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
            else:
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


filePath = "./boatsScrape.json"

with open(filePath, 'r') as file:
    ingestSettings = json.load(file)



shipPages = ingestSettings["shipPages"]

websiteRoot = ingestSettings["websiteRoot"]

maxNumberOfImagesForAShip = ingestSettings["maxNumberOfImagesForAShip"]
numberOfImagesForSubItems = ingestSettings["numberOfImagesForSubsItems"]


# BEGINS SCRAPING
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
            'description': description
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
