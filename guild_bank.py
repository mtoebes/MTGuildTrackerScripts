from settings import *
import re
import functools

POSSESSIONS_LUA_PATTERN = r= '"(?P<name>.+)",\r?\n\t*\[2] = ".*\\\\(?P<icon>.+)",\r?\n\t*\[3] = (?P<count>.*),\r?\n\t*\[4] = (?P<rarity>.*),\r?\n\t*\[6\] = "(?P<class>.*)",\r?\n\t*\[7\] = "(?P<subclass>.*)",\r?\n\t*\[8\] = "(?P<sufix_id>.*)",\r?\n\t*\[0\] = "(?P<id>.+)",'

IGNORE_BANK_ITEMS = [6948, 21544, 21543, 21539, 25, 38, 39, 40, 43, 44, 48, 5976, 5580, 2380, 2362, 6795, 1396, 57, 59, 6097]

def item_comp(a, b = None):
    if a["id"] == 999999:
        return -1
    elif b is None:
        return -1
    elif a["class"] < b["class"]:
        return -1
    elif a["class"] == b["class"]:
        if a["subclass"] < b["subclass"]:
            return -1
        elif a["subclass"] == b["subclass"]:
            if a["rarity"] > b["rarity"]:
                return -1
            elif a["rarity"] == b["rarity"]:
                return 1 if a["id"] > b["id"] else -1
            else:
                return 1
        else:
            return 1
    else:
        return 1


def item_comp_id(a, b = None):
    if a["id"] == 999999:
        return -1
    elif b is None:
        return -1
    elif a["rarity"] > b["rarity"]:
        return -1
    elif a["rarity"] == b["rarity"]:
        return 1 if a["id"] > b["id"] else -1
    else:
        return 1


def read_file():
    with open(POSSESSION_SAVED_VARIABLES_FILE_PATH) as lua_file:
        data = lua_file.read()
        item_dict = {}
        for match in re.finditer(POSSESSIONS_LUA_PATTERN, data):
            item_id = int(match.group("id"))
            if item_id in IGNORE_BANK_ITEMS:
                continue
            item_data = item_dict.get(item_id)
            if item_data is None:
                item_data = {
                    "count": int(match.group("count")),
                    "rarity": int(match.group("rarity")),
                    "name": match.group("name"),
                    "id": match.group("id"),
                    "icon": match.group("icon").lower(),
                    "class": match.group("class"),
                    "subclass": match.group("subclass")
                }
            else:
                item_data["count"] += int(match.group("count"))
            item_dict[item_id] = item_data

    gold = read_gold()

    item_dict[999999] = {
        "count": gold[0],
        "rarity": 1,
        "name": "Gold",
        "id": 999999,
        "icon": "INV_Misc_Coin_01".lower(),
        "class": "Money",
        "subclass": "Money"
    }
    return sorted(list(item_dict.values()),key=functools.cmp_to_key(item_comp))


def read_gold():
    with open(POSSESSION_SAVED_VARIABLES_FILE_PATH) as lua_file:
        data = lua_file.read()
        total_money = 0
        for match in re.finditer('\["money"\] = (?P<money>.*),', data):
            total_money += int(match.group("money"))
        copper = int(str(total_money)[-2:]) if len(str(total_money)) >= 1 else 0
        silver = int(str(total_money)[-4:-2]) if len(str(total_money)) >= 3 else 0
        gold =  int(str(total_money)[0:-4]) if len(str(total_money)) >= 5 else 0
        gold_list = [gold, silver, copper]
        return gold_list


def build_row(item):
    if item["class"] == item["subclass"]:
        classtype = item["class"]
    else:
        classtype = "{} - {}".format(item["class"], item["subclass"])

    if item["id"] == 999999:
        name = item["name"]
    else:
        name = HYPERLINK_FUNCTION_ITEM_FORMAT.format(item["id"], item["name"])
    return [item["count"],
            THUMBNAIL_FUNCTION_ITEM_FORMAT.format(item["icon"]) if ENABLE_ICONS else "",
            name,
            item["rarity"],
            classtype]


def set_header():
    cell_list = guild_bank_sheet.range('A2:E2')
    cell_values = ["Count", "Icon", "Name", "Rarity", "Type"]

    for i, val in enumerate(cell_values):
        cell_list[i].value = val

    guild_bank_sheet.update_cells(cell_list)


def set_date_header():
    today = datetime.datetime.now()
    date_string = today.strftime(MDY_TIMESTAMP_FORMAT)
    guild_bank_sheet.update_acell('C1', 'Last Updated = {}'.format(date_string))


def update_rows(list):
    build_rows = [build_row(item) for item in list]
    flat_list = [item for sublist in build_rows for item in sublist]

    range_string = 'A3:E{}'.format(len(build_rows)+2)
    cell_list = guild_bank_sheet.range(range_string)

    for i, val in enumerate(flat_list):
        cell_list[i].value = val

    guild_bank_sheet.update_cells(cell_list, value_input_option='USER_ENTERED')


def clear_sheet():
    guild_bank_sheet.clear()


def run():
    list = read_file()
    clear_sheet()
    set_date_header()
    set_header()
    update_rows(list)


if __name__ == "__main__":
    run()
