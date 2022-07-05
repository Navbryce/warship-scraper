from ABoatScraping.utilities.check_structure import check_structure

def valid_ship(ship):
    """
    makes sure the ship is valid

    returns object with keys: "missingKeys" and "wrongType"
    """
    return check_structure(ship, get_valid_ship(), "root")


def get_valid_ship():
    """
    returns a valid ship object used to verify the structure
    """
    return {
       "scrapeURL":"https://en.wikipedia.org/wiki/German_battleship_Scharnhorst",
       "configuration":"0",
       "displayName":"Scharnhorst",
       "name":" scharnhorst",
       "importantDates":{
       },
       "awards":[

       ],
       "armament":{
          "normalGun":{
               "sizeCalculate":{
               },
               "armaments":[
               ]
          },
          "torpedo":{
             "sizeCalculate":{
             },
             "armaments":[
             ]
          },
          "cannon":{
             "sizeCalculate":{
             },
             "armaments":[
             ]
          },
          "missile":{
             "sizeCalculate":{
             },
             "armaments":[
             ]
          }
       },
       "armor":{
          "armorObjects":[
          ],
          "calculations": {
          }
       },
       "description":"Scharnhorst was a German capital ship, alternatively described as a battleship and battlecruiser, of Nazi Germany's Kriegsmarine. She was the lead ship of her class, which included one other ship, Gneisenau. The ship was built at the Kriegsmarinewerft dockyard in Wilhelmshaven; she was laid down on 15 June 1935 and launched a year and four months later on 3 October 1936. Completed in January 1939, the ship was armed with a main battery of nine 28 cm (11 in) C/34 guns in three triple turrets.  Plans to replace these weapons with six 38 cm (15 in) SK C/34 guns in twin turrets were never carried out. ",
       "physicalAttributes":{
       },
       "pictures":[
       ],
       "class":"scharnhorst-class",
       "type":"battleship",
       "complement":1669.0,
    }
