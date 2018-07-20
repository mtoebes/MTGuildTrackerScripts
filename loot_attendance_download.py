from global_settings import *
import datetime
import util

# Run this script to download loot and attendance data from the google sheet into your tracker saved variables file.
# You must logout before running the script, otherwise the file will be overwritten when you logout.

LOOT_ENTRY_FORMAT = """
    ["{entry_key}"] = {{
        ["entry_key"] = "{entry_key}",
		["date"] = "{date}",
		["time_stamp"] = "{time_stamp}",
		["raid_id"] = "{raid_id}",
		["raid_name"] = "{raid_name}",
		["item_name"] = "{item_name}",
		["item_id"] = "{item_id}",
		["item_quality"] = "{item_quality}",
		["player_name"] = "{player_name}",
		["player_class"] = "{player_class}",
		["use_case"] = "{use_case}",
	}},"""

ATTENDANCE_ENTRY_FORMAT = """
    ["{player_name}"] = {{
        ["player_name"] = "{player_name}",
        ["player_class"] = "{player_class}",
        ["to_date"] = "{to_date}",
        ["last_5"] = "{last_5}",
        ["last_2_weeks"] = "{last_2_weeks}",
        ["last_4_weeks"] = "{last_4_weeks}",
    }},"""


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def to_loot_lua_entry(entry):
    return LOOT_ENTRY_FORMAT.format(**entry)


def to_attendance_lua_entry(entry):
    return ATTENDANCE_ENTRY_FORMAT.format(**entry)


def save_entries(loot_entries, attendance_entries):

    with open(TRACKER_SAVED_VARIABLES_FILE_PATH, 'r') as file:
        lines = file.readlines()

    with open('lua/build_backup.lua','w') as backup_file:
        backup_file.writelines(lines)

    with open(TRACKER_SAVED_VARIABLES_FILE_PATH, 'w') as file:
        file.write("\nMTGuildTrackerDB = {")
        for key, entry in loot_entries.items():
            file.write(to_loot_lua_entry(entry))
        file.write("\n}")

        file.write("\nMTGuildTracker_Attendance = {")
        for entry in attendance_entries:
            file.write(to_attendance_lua_entry(entry))
        file.write("\n}")

        file.write("\nMTGuildTracker_LastUpdate = {")
        file.write('\n\t["time_stamp"] = "{}"'.format( datetime.datetime.now().strftime(YMD_TIMESTAMP_FORMAT)))
        file.write("\n}")


def get_attendance_entries():
    loot_sheet_values = raid_attendance_sheet.get_all_values()

    cell_list = raid_attendance_sheet.range(8, 1, len(loot_sheet_values), 6)

    entries = []
    for chunk in chunks(cell_list, 6):
        if len(chunk[0].value) > 0:
            entries.append({
                "player_name": chunk[0].value,
                "player_class": chunk[1].value,
                "to_date": chunk[2].value[:-1],
                "last_4_weeks": chunk[3].value[:-1],
                "last_2_weeks": chunk[4].value[:-1],
                "last_5": chunk[5].value[:-1],

            })

    return entries


def run():
    print("Begin downloading loot history and raid attendance from the Google Sheet into the tracker saved variables file")
    print("Warning: You need to be logged out of account {} before running this".format(USER_ACCOUNT_NAME))
    loot_entries = util.get_loot_history_entries()
    attendance_entries = get_attendance_entries()
    save_entries(loot_entries, attendance_entries)
    print("Finished downloading loot history and raid attendance")


if __name__ == "__main__":
    run()
