
import urllib.request

from bs4 import BeautifulSoup
import re
from settings import *
import util
import sys

RAID_DATE_REGEX = '\((?P<date>.+)\)'

COLUMN_OFFSET = 5
ROW_OFFSET = 7

IGNORE_RAID_IDS = ['11327', '11335', '11328', '11316']
IGNORE_RAID_NAMES = ['ZG', 'AQ20', 'ONY']

MAX_COLUMN = 'CD'
OVERALL_FORMULA = '''=IF($A{row} <> "", SUM(ARRAYFORMULA(if(Y$1:{max_column}$1<>"",Y{row}:{max_column}{row},0)))/$C$2, "")'''
LAST_4_WEEKS_FORMULA ='''=SUM(ARRAYFORMULA(if($Y$1:${max_column}$1>=TODAY()-7*$D$2,$Y{row}:${max_column}{row},0)))/SUM(ARRAYFORMULA(if($Y$1:${max_column}$1>=TODAY()-7*$D$2,1,0)))'''
LAST_2_WEEKS_FORMULA='''=SUM(ARRAYFORMULA(if($Y$1:${max_column}$1>=TODAY()-7*$E$2,$Y{row}:${max_column}{row},0)))/SUM(ARRAYFORMULA(if($Y$1:${max_column}$1>=TODAY()-7*$E$2,1,0)))'''
LAST_5_FORMULA='''=IF($A{row} <> "", SUM(ARRAYFORMULA(IF(COLUMN(Y{row}:{max_column}{row})>=2*(COUNT(Y$1:{max_column}$1)-$F$2)+COLUMN($Y$1), IF(Y$1:{max_column}$1 <> "", Y{row}:{max_column}{row}, 0),0)))/$F$2, "")'''
LOOT_COUNT_FORMULA = '''=IF($A{row} <> "", SUM(ArrayFormula(IF('Raid Loot'!$H$2:$H=$A{row},IF('Raid Loot'!$B$2:$B=INDIRECT("R[{rel_mc}]C[-1]", false), 1,IF('Raid Loot'!$B$2:$B=INDIRECT("R[{rel_bwl}]C[-1]", false), 1,IF('Raid Loot'!$B$2:$B=INDIRECT("R[{rel_aq}]C[-1]", false), 1,0))), 0))), "")'''

attendance_players = util.get_recorded_attendance_players()
attendance_raid_ids = util.get_recorded_attendance_raid_ids()


class LegacyRaidAttendence():

    def __init__(self, raid_id=None,url=None):
        self.raid_id = raid_id

        if url:
            self.raid_url = url
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

    cell_list = raid_attendance_sheet.range(row, 1, row, 6)
    cell_list[0].value = player_name
    cell_list[1].value = player_class
    cell_list[2].value = OVERALL_FORMULA.format(row=row, max_column=MAX_COLUMN)
    cell_list[3].value = LAST_4_WEEKS_FORMULA.format(row=row, max_column=MAX_COLUMN)
    cell_list[4].value = LAST_2_WEEKS_FORMULA.format(row=row, max_column=MAX_COLUMN)

    raid_attendance_sheet.update_cells(cell_list, value_input_option='USER_ENTERED')

def add_raid_attendance(raid_column, raid_attendance):
    mark_row_list = []
    for player in raid_attendance.players:
        player_name = player[0]

        player_index = get_attendance_player_row(player_name)

        if player_index is None:
            player_index = len(attendance_players)
            add_new_player(player_index, player_name, player[1])

        mark_row_list.append(player_index)

    cell_list = raid_attendance_sheet.range(1, raid_column, len(attendance_players) + ROW_OFFSET, raid_column)

    cell_list[0].value = raid_attendance.raid_date

    if raid_attendance.raid_name_short == "AQ40":
        raid_offset = 5
    elif raid_attendance.raid_name_short == "BWL":
        raid_offset = 3
    else:
        raid_offset = 1

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


def is_official_raid(raid_attendance):
    date = datetime.datetime.strptime(raid_attendance.raid_date, MDY_TIMESTAMP_FORMAT)

    return util.is_official_raid(date, raid_attendance.raid_name) and raid_attendance.raid_name_short not in IGNORE_RAID_NAMES and raid_attendance.raid_id not in IGNORE_RAID_IDS


def add_raid(raid_attendance, override=False):
    if raid_attendance.raid_id not in attendance_raid_ids or override:
        column = get_next_column_index()
        add_raid_attendance(column, raid_attendance)
    else:
        print("skipping {}, already recorded".format(raid_attendance.raid_id))


def add_raid_id(raid_id):
    raid_attendance = LegacyRaidAttendence(raid_id)

    if is_official_raid(raid_attendance):
        print("adding {}".format(raid_id))
        add_raid(raid_attendance)
    else:
        print("skipping {}, not an official raid".format(raid_id))


def add_all_raids():
    for raid_id in util.get_legacy_raid_ids():
        add_raid_id(raid_id)


def get_raids_for_date(date):
    raid_attendance_list = []
    for raid_id in util.get_legacy_raid_ids():
        raid_attendance = LegacyRaidAttendence(raid_id)
        raid_date = datetime.datetime.strptime(raid_attendance.raid_date, MDY_TIMESTAMP_FORMAT)
        if  raid_date.date() == date.date():
            raid_attendance_list.append(raid_attendance)
        elif raid_date < date:
            break
    return raid_attendance_list

def get_raids_after_date(date):
    raid_attendance_list = []
    for raid_id in util.get_legacy_raid_ids():
        raid_attendance = LegacyRaidAttendence(raid_id)
        raid_date = datetime.datetime.strptime(raid_attendance.raid_date, MDY_TIMESTAMP_FORMAT)
        if raid_date.date() >= date.date():
            raid_attendance_list.append(raid_attendance)
        elif raid_date < date:
            break
    return raid_attendance_list


def add_raids_after_date(date):
    raid_attendance_list = get_raids_after_date(date)
    for raid in raid_attendance_list:
        add_raid(raid)


def add_raids_on_date(date):
    raid_attendance_list = get_raids_for_date(date)
    for raid in raid_attendance_list:
        add_raid(raid)


def add_raid_by_url(raid_id, url):
    raid_attendance = LegacyRaidAttendence(raid_id,url)
    add_raid(raid_attendance, True)


def add_new_raids():
    raid_dates = util.get_recorded_attendace_dates()
    last_raid_date = raid_dates[-1]
    add_raids_after_date(last_raid_date)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            date = datetime.datetime.strptime(arg, YMD_DATE_FORMAT)
            add_raids_on_date(date)
    else:
        add_new_raids()
