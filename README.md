
this readme is WIP

## Initial Setup

### Setup Oauth2 credentionals
  1. (see out of date steps here: http://gspread.readthedocs.io/en/latest/oauth2.html)
  1. Create a new google account to use for the guild. Sign into it.
  1. Go to Google Developers Console https://console.developers.google.com/project
  1. Click "Create Project", name it "<Guild Name> Tracker". Click create.
  1. From the navigation menu, go to "API & services" -> "credentials"
  1. Click "Create credentials", choose "Service account key" from the dropdown menu
      * Set the service account name to <Guild Name>CronJob
      * Set the Role to "Project" -> "Owner"
  1. Create and download the json file. Don't loss it!
        * Rename it to "guild_name_creds.json".
        * The name should be all lowercase and use underscores instead of spaces.
  1. From the navigation menu, go to "Dashboard", click "Enable APIS and Services"
  1. Search for and enable "Google Drive API" and "Gmail Sheets API"

### Setup the Google Sheet
  1. Make a copy of [this google sheet](https://docs.google.com/spreadsheets/d/1bWHOiqSNTIxd94vxGM6TU0JsaULuSRneZz3KpkWIayc/edit?usp=sharing),
  1. Rename it to: *\<Guild Name\> Tracker*. Do not rename or rearrange any of the sheets
  1. Open up the creds.json file you downloaded for the service account, copy the "client_email" value.
  1. Share the google sheet with that client email. Give it write permissions.

### Setup Python Project 
1. Download and install Python 3.6
    * [Windows instructions](https://docs.python.org/3/using/windows.html#installing-python)
    * [Mac instructions](https://docs.python.org/3/using/mac.html#installing-python)
    * Linux... If you don't know how, you probably shouldn't be on linux.
1. Download the [MTGuildTrackerScripts](https://github.com/mtoebes/MTGuildTrackerScripts)
    * If you are familiar with git, clone the project instead. 
    * If you want to start using git version control (trust me, you do), follow these steps to [install github desktop](https://help.github.com/desktop/guides/getting-started-with-github-desktop/installing-github-desktop/)
1. Optional: Download and install [PyCharm](https://www.jetbrains.com/pycharm/download). 
    * Once Pycharm is downloaded, open it and go to "file"->"open" and choose the folder you downloaded in the previous step 
1. Using your native terminal or the terminal in PyCharm, cd to the folder where you downloaded the project
    * run `pip install -r requirements.txt`
    * Python gurus: install to a new virtual environment


### Adjust User Specific Variables

Within the project there is a file called "user_settings.py". This should be the only file you need to alter in the project.
Any of the lines with a "\#TODO UPDATE PRIOR TO USE"  comment need to be set before you can run all of the scripts.