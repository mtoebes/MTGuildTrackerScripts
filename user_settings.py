# Below are all the user specific values that can be altered

### Account Settings ###

USER_ACCOUNT_NAME = 'my_account' #TODO UPDATE PRIOR TO USE
GUILD_BANK_ACCOUNT_NAME = 'guild_bank_account' #TODO UPDATE PRIOR TO USE


### File Settings ###

WORLD_OF_WARCRAFT_DIR = "E:\Games\World of Warcraft 1.12" #TODO UPDATE PRIOR TO USE
CREDS_FILE_NAME = 'fearless_creds.json'
TRACKER_SAVED_VARIABLES_FILE_NAME = 'FearlessTracker.lua'


### LegacyPlayer Settings ###

GUILD_NAME = 'Fearless'
GUILD_REALM = 'Northdale'


### Google Sheet Settings ###

# populates a column in the bank and loot sheets with an icon for that item (might be a performance hit to load the sheet)
ENABLE_ICONS = False
GOOGLE_SHEET_NAME = 'Fearless Tracker'
BANK_SHEET_INDEX = 0
LOOT_SHEET_INDEX = 1
ATTENDANCE_SHEET_INDEX = 2


### attendance_upload.py Settings ###

# Raid ids to ignore when uploading
IGNORE_RAID_IDS = []
# Raids names to ignore when uploading, such as "ZG" or "ONY"
IGNORE_RAID_NAMES = []


### bank_upload.py Settings ###

# Items to ignore when uploading the bank's contents, such as a hearthstone or currently equipped gear.
# Or you could be lazy and have your bank alt be a stripper.
IGNORE_BANK_ITEMS = [6948]

