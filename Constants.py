# pylint: disable=invalid-name  # it is normal to have the constants in a file named "Constants.py"
BOT_NAME = "FCT"

JSON_FOLDER = "jsons/"
YOUTUBE_PLAY_FOLDER = "youtube/"
# default is 25 MB because that is the max file size for discord for now.
# If you want to change this, make sure to check the current max upload limit for discord.
MAX_VIDEO_DOWNLOAD_SIZE: int = 25  # in MB, do not use anything other than an integer
