from lxml import cssselect
from lxml import html
import requests

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

    #print (infoBox.text_content())
    #Appends the ship to the list of ships
    ships.append(ship)
print(ships)
