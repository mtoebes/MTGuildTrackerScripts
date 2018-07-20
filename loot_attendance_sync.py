import loot_attendance_download
import loot_upload
import attendance_upload

# Performs all uploads and downloads required to sync loot and attendance data between the google sheet and the tracker addon.

if __name__ == "__main__":
    print("Begin sync")
    attendance_upload.add_recent_raids()
    loot_upload.run()
    loot_attendance_download.run()
    print("Finished sync")