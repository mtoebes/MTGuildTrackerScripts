import urllib.request
from bs4 import BeautifulSoup
import sys
from settings import *
import util
import re

LOOT_ROW_OFFSET = 1

ITEM_ICON_REGEX = ".*/(?P<img>\w+).jpg.*"
ITEM_NAME_REGEX = "(?P<name>.*) - Item"
ITEM_ID_REGEX =   '/Armory/Items/\?i=(?P<id>\d+)'
PLAYER_CLASS_REGEX = 'color-c(?P<index>\d+)'
RAID_DATE_REGEX = '\((?P<date>.+)\)'
# =CONCATENATE(TEXT((A13-DATE(1970,1,1))*86400+14400, "#"),"_",I13)
class LegacyRaidLoot:
    def __init__(self, raid_id):
        self.index = 0
        self.raid_id = raid_id
        self.raid_url = RAID_URL_FORMAT.format(raid_id)
        with urllib.request.urlopen(self.raid_url) as response:
            page = response.read()
        soup = BeautifulSoup(page, 'html.parser')

        overview = soup.find('div', attrs={'id':'info'}).contents[0]

        self.raid_name = overview.contents[0].strip()
        self.raid_date = re.match(RAID_DATE_REGEX, overview.contents[1].contents[0]).group('date')
        self.raid_date = datetime.datetime.strptime(self.raid_date, MDY_TIMESTAMP_ALT_FORMAT)

        fight_table = soup.find('table', attrs={'id': 'rs_loot'}).contents[1].contents
        self.items_dict = self.parse_raid(fight_table)

    def to_item_rows(self):
        rows = []
        for item_dict in self.items_dict:
            rows.append(self.to_item_row(item_dict))
        return rows

    def to_item_row(self, item_dict):
        return [
            item_dict['item_date'].strftime("%m/%d/%Y"),
            self.raid_id,
            HYPERLINK_FUNCTION_FORMAT.format(self.raid_url, self.raid_name),
            item_dict['item_date'].strftime("%m/%d/%Y %H:%M:%S"),
            THUMBNAIL_FUNCTION_ITEM_FORMAT.format(item_dict['item_icon']),
            HYPERLINK_FUNCTION_ITEM_FORMAT.format(item_dict['item_id'], item_dict['item_name']),
            item_dict['item_quality'],
            item_dict['player_name'],
            item_dict['player_class'],
            item_dict['item_id'],
            "{}_{}".format(item_dict['item_date'].time(), item_dict['item_id'] )
        ]

    def parse_raid(self, fight_table):
        items_dict = []
        if fight_table is not None:
            for fight in fight_table:
                items_dict.extend(self.parse_raid_fight(fight))
        return items_dict

    def parse_raid_fight(self, fight):
        boss_name = fight.contents[0].next
        boss_dict = {
            'boss_name': boss_name,
        }

        fight_inv = fight.contents[1].contents

        items_dict = []
        if fight_inv is not None:
            for item in fight_inv:
                item_dict = self.parse_raid_fight_item(item)
                if item_dict is not None:
                    item_dict.update(boss_dict)
                    items_dict.append(item_dict)
        return items_dict

    def parse_raid_fight_item(self, item):
        item_id = re.match(ITEM_ID_REGEX, item.contents[0].attrs["href"]).group('id')

        group_match =  re.match(ITEM_ICON_REGEX, item.attrs['style'])
        if group_match:
            item_icon = group_match.group('img')
        else:
            item_icon = 'inv_misc_questionmark'

        item_quality = 'epic' # item.find('div', attrs={'class': 'quality'}).attrs['id']
        item_link = ITEM_URL_FORMAT.format(item_id)

        player_class = PLAYER_CLASSES[int(re.match(PLAYER_CLASS_REGEX,item.contents[2].attrs['class'][0]).group('index'))]
        player_name = item.contents[2].next

        with urllib.request.urlopen(item_link) as response:
            soup = BeautifulSoup(response.read(), 'html.parser')
        name = re.match(ITEM_NAME_REGEX, soup.find('div', attrs={'id': 'header'}).contents[1].contents[3].next).group('name')
        self.index = self.index + 1
        return {
            'index':self.index,
            'item_name': name,
            'item_icon': item_icon,
            'item_id': item_id,
            'item_link': item_link,
            'item_quality': item_quality,
            'player_name': player_name,
            'player_class': player_class,
            'item_date': self.raid_date + datetime.timedelta(0,self.index)
        }

def get_legacy_raid_ids():
    with urllib.request.urlopen(HYPERLINK_FUNCTION_LEGACY_PLAYER_RAIDS) as response:
        page = response.read()
    soup = BeautifulSoup(page, 'html.parser')
    character_table_list = soup.find('table', attrs={'class':'table noborder bbdesign'}).contents[1].contents

    raid_ids = []
    for element in character_table_list:
        raid_id = element.contents[0].contents[0]
        if raid_id:
            raid_ids.append(raid_id)
    return raid_ids

def add_raid_loot(raid_loot, index=0):

    raid_loot_info = raid_loot.to_item_rows()
    if raid_loot_info:
        cell_list = raid_loot_sheet.range(index + LOOT_ROW_OFFSET + 1, 1, index + LOOT_ROW_OFFSET + 1+ len(raid_loot_info), len(raid_loot_info[0]))

        flat_list = [item for sublist in raid_loot_info for item in sublist]
        for i, val in enumerate(flat_list):
            cell_list[i].value = val
        raid_loot_sheet.update_cells(cell_list, value_input_option='USER_ENTERED')

def get_last_index():
    return len([raid_id for raid_id in raid_loot_sheet.col_values(2) if raid_id != ''][1:])

def update_missing_icons():
    item_column = raid_loot_sheet.col_values(6, value_render_option='FORMULA')[1:]

    for row, item in enumerate(item_column):
        if item:
            print(row)
            if row < len(icon_column):
                icon = icon_column[row]
            else:
                icon = ""
            if not icon:
                item_id = re.match(HYPERLINK_FUNCTION_ITEM_REGEX, item).groups()[0]
                item_icon = util.get_item_icon(item_id)
                icon_link = THUMBNAIL_FUNCTION_ITEM_FORMAT.format(item_icon)
                raid_loot_sheet.update_cell(row + 2, 5, icon_link)
                print(row)

def add_raid_id(raid_id):
    index = get_last_index()
    if raid_id not in util.get_recorded_loot_raid_ids():
        raid_loot = LegacyRaidLoot(raid_id)
        if not util.is_20_man_raid(raid_loot.raid_name):
            add_raid_loot(raid_loot, index)

def add_all_raids():
    for raid_id in get_legacy_raid_ids():
        add_raid_id(raid_id)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            add_raid_id(arg)
    else:
        add_all_raids()