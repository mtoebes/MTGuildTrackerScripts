
import meme_tracker_build
import meme_tracker_parse
import util
from util import *
import raid_attendance
if __name__ == "__main__":
    print("Add Raid Attendance")
    raid_attendance.add_recent_raids()
    print("Upload Loot History from MemeTracker")
    meme_tracker_parse.run()
    print("Download Loot History and Raid Attendance to MemeTracker")
    meme_tracker_build.run()
