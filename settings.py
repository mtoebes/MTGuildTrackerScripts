import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

today = datetime.datetime.now()

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)

client = gspread.authorize(creds)

guild_bank_sheet = client.open("Guild Tracker").get_worksheet(0)
raid_loot_sheet = client.open("Guild Tracker").get_worksheet(2)
raid_attendance_sheet = client.open("Guild Tracker").get_worksheet(3)

SAVED_VARIABLES_FILE_PATH = 'E:\Games\World of Warcraft 1.12\WTF\Account\{}\SavedVariables\{}'

POSSESSION_SAVED_VARIABLES_FILE_PATH = SAVED_VARIABLES_FILE_PATH.format("BANKOFMEMES", "Possessions.lua")
MEME_TRACKER_SAVED_VARIABLES_FILE_PATH = SAVED_VARIABLES_FILE_PATH.format("MTOEBES", "MemeTracker.lua")

THUMBNAIL_FUNCTION_FORMAT = '=IMAGE("{}")'
HYPERLINK_FUNCTION_FORMAT = '=HYPERLINK("{}","{}")'

PLAYER_CLASSES = ["warrior", "rogue", "priest", "hunter", "druid", "mage", "warlock", "paladin"]

RAID_NAME_SHORT = {
    'Blackwing Lair': 'BWL',
    'Molten Core': 'MC',
    'Zul\'Gurub':'ZG',
    'Onyxia\'s Lair':'ONY',
    "Ahn'Qiraj":'AQ40',
    "Ruins of Ahn'Qiraj":"AQ20"
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
YMD_DATE_FORMAT = "%y-%m-%d"
MDY_DATE_FORMAT = "%m/%d/%Y"

HYPERLINK_FUNCTION_ITEM_REGEX = '=HYPERLINK\("http://vanillawowdb.com/\?item=(.*)","(.*)"\)'


THUMBNAIL_FUNCTION_ITEM_FORMAT = '=IMAGE("http://vanillawowdb.com/images/icons/large/{}.png")'
HYPERLINK_FUNCTION_ITEM_FORMAT = '=HYPERLINK("http://vanillawowdb.com/?item={}","{}")'
HYPERLINK_FUNCTION_REALM_PLAYER_FORMAT = '=HYPERLINK("http://realmplayers.com/CharacterViewer.aspx?realm=Ely&player={}","{}")'

HYPERLINK_FUNCTION_LEGACY_PLAYER_RAIDS = 'https://legacyplayers.com/Raids/?name=meme%20team&exp=0'

CLASSIC_DB_URL_FORMAT = "https://classicdb.ch/?item={}"
ITEM_URL_FORMAT = 'http://vanillawowdb.com/?item={}-0'
RAID_URL_FORMAT = 'https://legacyplayers.com/Raids/Viewer/?id={}'