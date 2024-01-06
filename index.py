#   @author:SpiralAPI
#   @description: Mass download all games in a respective group, granted you have edit permissions.
#   @date: 5/2/2023

# IMPORTS
import requests
import unicodedata
import re
import os
import sys

# VARIABLES
gamesFolder = "games"
assetDownloadEndpoint = "https://assetdelivery.roblox.com/v1/asset/?id=" # main endpoint to download assets

# FUNCTIONS
def validateCookie(cookie: str) -> bool: # pretty self explanatory, validates if the cookie works
    headers = {"cookie": f".ROBLOSECURITY={cookie}"}
    response = requests.get(
        "https://www.roblox.com/mobileapi/userinfo", headers=headers
    )
    try:
        if response.json()["UserID"]:
            return True
    except:
        return False


def validateGroup(groupId: int) -> bool: # validates a group exists
    response = requests.get(
        f"https://groups.roblox.com/v2/groups?groupIds={str(groupId)}"
    )
    try:
        if response.json()["data"][0]["id"]:
            return True
    except:
        return False


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def returnGamesList(groupID): # returns all games under a group
    cursor = "" # used to search through multiple pages
    complete = False

    finalReturn = list()

    while complete == False:
        response = requests.get(
            f"https://games.roblox.com/v2/groups/{groupID}/games?limit=100&cursor={cursor}"
        )
        data = response.json()["data"]

        if (
            (response.json()["nextPageCursor"] == "null")
            or (response.json()["nextPageCursor"] == None)
            or (response.json()["nextPageCursor"] == "None")
        ):
            complete = True
        else:
            complete = False
            cursor = response.json()["nextPageCursor"]

        for Game in data:
            finalReturn.append(dict(name=Game["name"], id=Game["rootPlace"]["id"]))

    return finalReturn


def saveGameFile(Name, placeId, groupId, cookie): # saves a game file by its placeid and cookie
    response = requests.get(
        assetDownloadEndpoint + str(placeId),
        headers={"cookie": f".ROBLOSECURITY={cookie}"},
    )

    with open(f"{gamesFolder}/{str(groupId)}_{slugify(Name)}.rbxl", "ab") as file:
        file.write(response.content)
        return f"{str(groupId)}_{slugify(Name)}.rbxl"


def clearConsole(): # visuals
    os.system("cls" if os.name == "nt" else "clear")
    print(
        """
:'######::'########::'####:'########:::::'###::::'##::::::::
'##... ##: ##.... ##:. ##:: ##.... ##:::'## ##::: ##::::::::
 ##:::..:: ##:::: ##:: ##:: ##:::: ##::'##:. ##:: ##::::::::
. ######:: ########::: ##:: ########::'##:::. ##: ##::::::::
:..... ##: ##.....:::: ##:: ##.. ##::: #########: ##::::::::
'##::: ##: ##::::::::: ##:: ##::. ##:: ##.... ##: ##::::::::
. ######:: ##::::::::'####: ##:::. ##: ##:::: ##: ########::
:......:::..:::::::::....::..:::::..::..:::::..::........:::
:::::::::::::::::MASS GROUP GAME DOWNLOADER:::::::::::::::::\n\n
"""
    )


# FUNCTIONALITY
if not os.path.exists(gamesFolder): # ensure that the games folder exists
    os.makedirs(gamesFolder)

clearConsole()

tempCookieValid = False
cookieVar = ""
while tempCookieValid == False: # inputs to make the experience better
    cookie = input("Please enter your ROBLOX Cookie (type 'exit' to quit): ")
    if cookie == "exit":
        clearConsole()
        sys.exit("Quitting program.")
    else:
        if validateCookie(cookie) == True:
            tempCookieValid = True
            cookieVar = cookie
        else:
            print("Invalid cookie. Please try again.")

clearConsole()

tempGroupValid = False
finalGroupId = 0
while tempGroupValid == False: # more inputs
    group = input("Please enter the target Group ID (type 'exit' to quit): ")
    if group == "exit":
        clearConsole()
        sys.exit("Quitting program.")
    else:
        if validateGroup(group) == True:
            tempGroupValid = True
            finalGroupId = group
        else:
            print("Invalid Group ID. Please try again.")

clearConsole()

Games = returnGamesList(finalGroupId) # returns a list of all games in a group 
for Game in Games:
    fileName = saveGameFile(Game["name"], Game["id"], finalGroupId, cookieVar) # the final loop, which will download all games!
    print(f"Successfully saved game file {fileName}")

print("DOWNLOAD COMPLETE. EXITING PROGRAM.")
