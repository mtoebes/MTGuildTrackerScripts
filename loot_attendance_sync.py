import loot_attendance_download
import loot_upload
import attendance_upload


if __name__ == "__main__":
    print("Upload Attendance History from Legacy")
    attendance_upload.add_recent_raids()
    print("Upload Loot History from MemeTracker")
    loot_upload.run()
    print("Download Loot History and Raid Attendance to MemeTracker")
    loot_attendance_download.run()
