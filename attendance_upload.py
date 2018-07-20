import urllib.request
from bs4 import BeautifulSoup
import re
from global_settings import *
import util
import argparse
import functools
import operator

# Run this script to upload attendance data from legacy players into google sheets.
# You can upload raids by specifying a raid id, date, or url.

RAID_DATE_REGEX = '\((?P<date>.+)\)'

COLUMN_OFFSET = 5
ROW_OFFSET = 10

attendance_players = util.get_recorded_attendance_players()
attendance_raid_ids = util.get_recorded_attendance_raid_ids()

skip_player_list = []

class LegacyRaidAttendence():

    def __init__(self, raid_id=None,url=None):
        self.raid_id = raid_id

        if url:
            self.raid_url = url
            self.raid_id = re.match(RAID_URL_REGEX, url).groups()[0]
        else:
            self.raid_url = RAID_URL_FORMAT.format(raid_id)

        with urllib.request.urlopen(self.raid_url) as response:
            page = response.read()
        soup = BeautifulSoup(page, 'html.parser')
        overview = soup.find('div', attrs={'id':'info'}).contents[1]

        participant_list = soup.find('table', attrs={'id': 'rs_participants'}).contents[3].contents[1:9]

        self.players = set()
        for index, class_list in enumerate(participant_list):
            player_class = PLAYER_CLASSES[index]
            try:
                class_list = class_list.contents[0].contents
                for player in [class_list[i] for i in range(len(class_list)) if i % 2 == 1]:
                    player_name = player.next
                    self.players.add((player_name, player_class))
            except:
                continue
        self.raid_name = overview.contents[0].strip()

        self.raid_name_short = RAID_NAME_SHORT.get(self.raid_name, self.raid_name)
        self.raid_date = re.match(RAID_DATE_REGEX, overview.contents[1].contents[0]).group('date')
        self.raid_date = datetime.datetime.strptime(self.raid_date, MDY_TIMESTAMP_ALT_FORMAT).strftime(MDY_TIMESTAMP_FORMAT)

    def __str__(self):
        date = datetime.datetime.strptime(self.raid_date, MDY_TIMESTAMP_FORMAT).strftime(YMD_DATE_FORMAT)
        return "{short_name} {date} {id}".format(id=self.raid_id, short_name=self.raid_name_short, date=date)


def get_player_guild(player_name):

    search_url = PLAYER_SEARCH_URL_FORMAT.format(player_name)
    with urllib.request.urlopen(search_url) as response:
        page = response.read()
    soup = BeautifulSoup(page, 'html.parser')
    player_table = soup.find('table', attrs={'id':'player'})

    player_list = player_table.contents[3].contents

    if len(player_list) <= 1:
        return None

    for row in player_list[1:-1]:
        realm = row.contents[2].contents[0]

        if realm == GUILD_REALM:
            guild_wrapper = row.contents[1].contents[0]
            guild = guild_wrapper.contents[0] if len(guild_wrapper) > 0 else None
            return guild

    return None

def get_next_column_index():
    header_row = raid_attendance_sheet.row_values(1)

    dates = [date for date in header_row if date !=''][COLUMN_OFFSET:]
    date_count = len(dates)

    column = COLUMN_OFFSET + date_count + 1
    return column


def get_attendance_player_row(player_name):
    for idx, player in enumerate(attendance_players):
        if player == player_name:
            return idx
    return None


def add_new_player(player_index, player_name, player_class):
    row = player_index + ROW_OFFSET + 1
    attendance_players.append(player_name)

    cell_list = raid_attendance_sheet.range(row, 1, row, 2)
    cell_list[0].value = player_name
    cell_list[1].value = player_class

    raid_attendance_sheet.update_cells(cell_list, value_input_option='USER_ENTERED')

def add_new_players(new_players):
    player_index = len(attendance_players)
    row = player_index + ROW_OFFSET + 1
    cell_list = raid_attendance_sheet.range(row, 1, row + len(new_players), 2)

    for index, new_player in enumerate(new_players):
        cell_list[2*index].value = new_player[0]
        cell_list[2*index+1].value = new_player[1]
        attendance_players.append(new_player[0])

    raid_attendance_sheet.update_cells(cell_list, value_input_option='USER_ENTERED')


def add_raid_attendance(raid_column, raid_attendance):
    mark_row_list = []

    new_players = []

    for player in raid_attendance.players:
        player_name = player[0]

        player_index = get_attendance_player_row(player_name)

        if player_index is None:
            if player_name not in skip_player_list:
                player_guild = get_player_guild(player_name)
                if player_guild != GUILD_NAME:
                    skip_player_list.append(player_name)
                    print("Skipping attendance for {} from [{}]".format(player_name, player_guild))
                else:
                    player_index = len(attendance_players) + len(new_players)
                    new_players.append((player_name, player[1]))

        mark_row_list.append(player_index)

    add_new_players(new_players)

    cell_list = raid_attendance_sheet.range(1, raid_column, len(attendance_players) + ROW_OFFSET, raid_column)

    cell_list[0].value = raid_attendance.raid_date

    if raid_attendance.raid_name_short == "AQ40":
        raid_offset = 6
    elif raid_attendance.raid_name_short == "BWL":
        raid_offset = 4
    elif raid_attendance.raid_name_short == "Naxx":
        raid_offset = 8
    else:
        raid_offset = 2

    cell_list[raid_offset].value = HYPERLINK_FUNCTION_FORMAT.format(raid_attendance.raid_url, raid_attendance.raid_name_short)
    cell_list[raid_offset+1].value = raid_attendance.raid_id

    for index, val in enumerate(cell_list):
        if index >= ROW_OFFSET:
            player_index = index - ROW_OFFSET
            if player_index in mark_row_list:
                cell_list[index].value = '1'
            else:
                cell_list[index].value = ''

    raid_attendance_sheet.update_cells(cell_list, value_input_option='USER_ENTERED')


def add_raid(raid_attendance, override):
    if not util.is_official_raid(raid_attendance.raid_name_short, raid_attendance.raid_id) and not override:
        print("Skipping Unofficial Raid: {}. ".format(raid_attendance))
        return
    elif raid_attendance.raid_id in attendance_raid_ids and not override:
        print("Skipping Recorded Raid: {}.".format(raid_attendance))
    else:
        print("Adding New Raid: {}.".format(raid_attendance, override))
        column = get_next_column_index()
        add_raid_attendance(column, raid_attendance)


def add_raid_by_id(raid_id, override=False):
    raid_attendance = LegacyRaidAttendence(raid_id)
    add_raid(raid_attendance, override)


def add_raids_by_date(date, override=False):
    raid_attendance_list = []
    for raid_id in util.get_legacy_raid_ids():
        raid_attendance = LegacyRaidAttendence(raid_id)
        raid_date = datetime.datetime.strptime(raid_attendance.raid_date, MDY_TIMESTAMP_FORMAT)
        if raid_date.date() == date.date():
            raid_attendance_list.append(raid_attendance)
        elif raid_date < date:
            break

    for raid in raid_attendance_list:
        add_raid(raid, override)


def add_raid_by_url(url, override=False):
    raid_attendance = LegacyRaidAttendence(None, url)
    add_raid(raid_attendance, override)


def add_raids_after_date(date, override=False):
    raid_attendance_list = []
    for raid_id in util.get_legacy_raid_ids():
        raid_attendance = LegacyRaidAttendence(raid_id)
        raid_date = datetime.datetime.strptime(raid_attendance.raid_date, MDY_TIMESTAMP_FORMAT)
        if raid_date.date() >= date.date():
            raid_attendance_list.append(raid_attendance)
        elif raid_date < date:
            break

    def item_comp(a, b=None):
        return a.raid_date < b.raid_date

    def item_comp2(a, b=None):
        return a.raid_date > b.raid_date

    for raid in sorted(raid_attendance_list, key=operator.attrgetter('raid_date')):
        add_raid(raid, override)


def add_all_raids(override=False):
    for raid_id in util.get_legacy_raid_ids():
        add_raid_by_id(raid_id, override)


def add_recent_raids():
    print("Begin uploading attendance history from legacyplayers into the Google Sheet")

    raid_dates = util.get_recorded_attendance_dates()
    if len(raid_dates) > 0:
        last_raid_date = raid_dates[-1]
    else:
        last_raid_date = datetime.datetime.strptime("18-01-01", YMD_DATE_FORMAT)
    add_raids_after_date(last_raid_date)

    print("Finished uploading Attendance history")


def parse_date_string(date_str):
    parsed_date = None

    if not parsed_date:
        try:
            parsed_date = datetime.datetime.strptime(date_str, YMD_DATE_FORMAT)
        except ValueError:
            parsed_date = None
    if not parsed_date:
        try:
            parsed_date = datetime.datetime.strptime(date_str, YMD_DATE_LONG_FORMAT)
        except ValueError:
            parsed_date = None

    if not parsed_date:
        try:
            parsed_date = datetime.datetime.strptime(date_str, MDY_DATE_FORMAT)
        except ValueError:
            parsed_date = None
    if not parsed_date:
        try:
            parsed_date = datetime.datetime.strptime(date_str, MDY_DATE_LONG_FORMAT)
        except ValueError:
            parsed_date = None
    if not parsed_date:
        try:
            parsed_date = datetime.datetime.strptime(date_str, "%m/%d").replace(year=datetime.datetime.now().year)
        except ValueError:
            parsed_date = None
    if not parsed_date:
        try:
            parsed_date = datetime.datetime.strptime(date_str, "%m-%d").replace(year=datetime.datetime.now().year)
        except ValueError:
            print ("ERROR: Unable to parse Date: {}".format(date_str))
    return parsed_date


if __name__ == "__main__":
    print("Begin uploading attendance history from legacyplayers into the Google Sheet")

    parser = argparse.ArgumentParser()
    parser.add_argument('--after_date', '-a', type=str)
    parser.add_argument('--date', '-d', type=str)
    parser.add_argument('--id', '-i', type=str)
    parser.add_argument('--url', '-u', type=str)
    parser.add_argument('--force', '-f', type=bool, default=False)

    args = parser.parse_args()

    if args.id:
        print("Uploading raids by ID: {}".format(args.id))
        add_raid_by_id(args.id, args.force)
    elif args.url:
        print("Uploading raids by URL: {}".format(args.url))
        add_raid_by_url(args.url, args.force)
    elif args.date:
        print("Uploading raids by date: {} (Older dates will take longer to upload)".format(args.date))
        date = parse_date_string(args.date)
        if date:
            add_raids_by_date(date, args.force)
    elif args.after_date:
        print("Uploading raids on/after date: {} (Older dates will take longer to upload)".format(args.after_date))
        date = parse_date_string(args.after_date)
        if date:
            add_raids_after_date(date, args.force)
    else:
        raid_dates = util.get_recorded_attendance_dates()
        if len(raid_dates) > 0:
            last_raid_date = raid_dates[-1]
            print("Uploading raids since most recent raid date: {} (Older dates will take longer to upload)".format(last_raid_date, args.force))
            add_raids_after_date(last_raid_date)

    print("Finished uploading attendance history")
