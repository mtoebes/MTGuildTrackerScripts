import loot_attendance_download
import loot_upload
import attendance_upload

# Performs all uploads and downloads required to sync loot and attendance data between the google sheet and the tracker addon.

if __name__ == "__main__":
    print("Sync Begin")
    print("Uploading Attendance History from legacyplayers")
    attendance_upload.add_recent_raids()
    print("Uploading Loot History from SavedVariables File")
    loot_upload.run()
    print("Downloading Loot History and Raid Attendance to SavedVariables File")
    loot_attendance_download.run()
    print("Sync Complete")