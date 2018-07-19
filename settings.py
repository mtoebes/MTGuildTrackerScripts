import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from urllib.parse import quote
from pathlib import Path

### User specific values that must be set ###

GUILD_NAME = 'guild name'
USER_ACCOUNT_NAME = 'my_account'
GUILD_BANK_ACCOUNT_NAME = 'bank_account'
WORLD_OF_WARCRAFT_DIR = "E:\Games\World of Warcraft 1.12"
ENABLE_ICONS = False

### DO NOT EDIT VALUES BELOW THIS POINT ###

CREDS_FILE_NAME = "creds.json"

POSSESSION_SAVED_VARIABLES_FILE_PATH = Path("{}/WTF/Account/{}/SavedVariables/{}".format(WORLD_OF_WARCRAFT_DIR, GUILD_BANK_ACCOUNT_NAME, "Possessions.lua"))
MEME_TRACKER_SAVED_VARIABLES_FILE_PATH =  Path("{}/WTF/Account/{}/SavedVariables/{}".format(WORLD_OF_WARCRAFT_DIR, USER_ACCOUNT_NAME, "MemeTracker.lua"))

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE_NAME, scope)

client = gspread.authorize(creds)

GOOGLE_SHEET_NAME = "{} Guild Tracker".format(GUILD_NAME)

guild_bank_sheet = client.open(GOOGLE_SHEET_NAME).get_worksheet(0)
raid_loot_sheet = client.open(GOOGLE_SHEET_NAME).get_worksheet(2)
raid_attendance_sheet = client.open(GOOGLE_SHEET_NAME).get_worksheet(3)

THUMBNAIL_FUNCTION_FORMAT = '=IMAGE("{}")'
HYPERLINK_FUNCTION_FORMAT = '=HYPERLINK("{}","{}")'

PLAYER_CLASSES = ["warrior", "rogue", "priest", "hunter", "druid", "mage", "warlock", "paladin"]

RAID_NAME_SHORT = {
    'Blackwing Lair': 'BWL',
    'Molten Core': 'MC',
    'Zul\'Gurub':'ZG',
    'Onyxia\'s Lair':'ONY',
    "Ahn'Qiraj":'AQ40',
    "Ruins of Ahn'Qiraj":"AQ20",
    "Naxxramas":"Naxx",
}

CLASS_COLORS = {
    '9482ca': 'warlock',
    '69ccf0': 'mage',
    'CCC': 'unknown',
    'f58cba': 'paladin',
    'c79c6e': 'warrior',
    'fff569': 'rogue',
    'abd473': 'hunter',
    'ff7d0a': 'druid',
    'ffffff': 'priest', }


MDY_TIMESTAMP_FORMAT = "%m/%d/%Y %H:%M:%S"

MDY_TIMESTAMP_ALT_FORMAT = '%m/%d/%Y %I:%M %p'
MDY_TIMESTAMP_ALT2_FORMAT = '%m/%d/%Y %I:%M:%S %p'

YMD_TIMESTAMP_FORMAT = "%y-%m-%d %H:%M:%S"

YMD_DATE_LONG_FORMAT = "%Y-%m-%d"
YMD_DATE_FORMAT = "%y-%m-%d"
MDY_DATE_LONG_FORMAT = "%m/%d/%Y"
MDY_DATE_FORMAT = "%m/%d/%y"

HYPERLINK_FUNCTION_ITEM_REGEX = '=HYPERLINK\("http://vanillawowdb.com/\?item=(.*)","(.*)"\)'
RAID_URL_REGEX = 'https://legacyplayers.com/Raids/Viewer/\?id=(\d+).*'

THUMBNAIL_FUNCTION_ITEM_FORMAT = '=IMAGE("http://vanillawowdb.com/images/icons/large/{}.png")'
HYPERLINK_FUNCTION_ITEM_FORMAT = '=HYPERLINK("http://vanillawowdb.com/?item={}","{}")'

HYPERLINK_FUNCTION_LEGACY_PLAYER_RAIDS = 'https://legacyplayers.com/Raids/?name={}&exp=0'.format(quote(GUILD_NAME))

CLASSIC_DB_URL_FORMAT = "https://classicdb.ch/?item={}"
ITEM_URL_FORMAT = 'http://vanillawowdb.com/?item={}-0'
RAID_URL_FORMAT = 'https://legacyplayers.com/Raids/Viewer/?id={}'