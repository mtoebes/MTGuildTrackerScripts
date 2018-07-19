import util
from settings import *
import re

TRACKER_DB_START_PATTERN = """MTGuildTrackerDB = {"""
LOOT_HISTORY_START_PATTERN = """.*\["(?P<entry_key>.*)"] = {"""
LOOT_HISTORY_FIELD_PATTERN = """.*\["(?P<name>.*)"] = "(?P<value>.*)","""
LOOT_HISTORY_END_PATERN = """.*},"""
TRACKER_DB_END_PATTERN = """}"""

RECORD_FORMAT = '{date}\t\t{raid_name}\t{time_stamp}\t=IMAGE("http://vanillawowdb.com/images/icons/large/{item_icon}.png")\t=HYPERLINK("http://vanillawowdb.com/?item={item_id}","{item_name}")\t{item_quality}\t=HYPERLINK("http://realmplayers.com/CharacterViewer.aspx?realm=Ely&player={player_name}","{player_name}")\t{player_class}\t{item_id}\t{entry_key}'

def get_last_index():
    return len([raid_id for raid_id in raid_loot_sheet.col_values(2) if raid_id != ''][1:])

def get_entry_dict(find):
    find_iter = re.finditer(LOOT_HISTORY_FIELD_PATTERN, find[1])

    entry_dict = {}
    for item in find_iter:
        entry_dict[item.group("name")] = item.group("value")

    entry_dict["time_stamp"] = datetime.datetime.strptime(entry_dict["time_stamp"], YMD_TIMESTAMP_FORMAT).strftime(MDY_TIMESTAMP_FORMAT)
    entry_dict["date"] = datetime.datetime.strptime(entry_dict["date"], YMD_DATE_FORMAT)

    return entry_dict


def parse_tracker_file():

    with open(TRACKER_SAVED_VARIABLES_FILE_PATH, 'r') as file:
        lines = file.readlines()

    with open('lua/parse_backup.lua','w') as backup_file:
        backup_file.writelines(lines)

    found_start = False
    found_end = False
    entries = {}

    entry_dict = {}

    for line in lines:
        if re.match(TRACKER_DB_START_PATTERN, line):
            found_start = True
        elif re.match(TRACKER_DB_END_PATTERN, line) and found_start:
            found_end = True
        elif found_start and not found_end:
            if re.match(LOOT_HISTORY_START_PATTERN, line):
                entry_dict["entry_key"]=  re.match(LOOT_HISTORY_START_PATTERN, line).group("entry_key")
            elif re.match(LOOT_HISTORY_FIELD_PATTERN, line):
                item = re.match(LOOT_HISTORY_FIELD_PATTERN, line)
                entry_dict[item.group("name")] = item.group("value")
            elif re.match(LOOT_HISTORY_END_PATERN, line):
                if not entry_dict.get("entry_key"):
                    entry_dict["entry_key"] = "{}_{}".format(int(datetime.datetime.strptime(entry_dict['time_stamp'],YMD_TIMESTAMP_FORMAT ).timestamp()), entry_dict['item_id'] )
                entries[entry_dict["entry_key"]] = dict(entry_dict)
                entry_dict = {}
    return entries


def add_entry(index, entry, dryrun=False):

    print("add_entry {} {}".format(index, entry))
    if not dryrun:
        cell_list = raid_loot_sheet.range(index+1, 1, index+1, 12)
        cell_list[0].value = entry['date']
        cell_list[1].value = entry['raid_name']
        cell_list[2].value = entry['player_name']
        cell_list[3].value = entry['player_class']
        cell_list[4].value = THUMBNAIL_FUNCTION_ITEM_FORMAT.format( util.get_item_icon(entry["item_id"])) if ENABLE_ICONS else ""
        cell_list[5].value = HYPERLINK_FUNCTION_ITEM_FORMAT.format(entry['item_id'], entry['item_name'])
        cell_list[6].value = entry.get('use_case', "MS")
        cell_list[7].value = entry['time_stamp']
        cell_list[8].value = entry['item_quality']
        cell_list[9].value = entry['item_id']
        cell_list[10].value = entry.get('raid_id',"")
        cell_list[11].value = entry['entry_key']
        raid_loot_sheet.update_cells(cell_list, value_input_option='USER_ENTERED')


def update_entry(index, entry):
    #print("update_entry {} {}".format(index, entry))
    return


def get_new_entries():
    loot_history_entries = util.get_loot_history_entries(True)

    index = len(raid_loot_sheet.col_values(1))
    file_entries = parse_tracker_file()

    new_entries = []

    for entry_key, entry_dict in file_entries.items():

        loot_history_entry = loot_history_entries.get(entry_key)

        if loot_history_entry:
            update_entry(loot_history_entry['index'], entry_dict)
        else:
            print(index)
            add_entry(index, entry_dict)
            index += 1

    return new_entries


def run():
    get_new_entries()


if __name__ == "__main__":
    run()
