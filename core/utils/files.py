# Python
from os.path import isfile

MEDIA_FOLDER_PATH = \
    "/home/nekofetishist/Desktop/Projects/roommate_app/roommate_bot/media"


def is_photo_exist(user_id: int) -> bool:
    return isfile(
        path=f"{MEDIA_FOLDER_PATH}/photos/users/{user_id}.jpg"
    )


def get_photo_path(user_id: int) -> str:
    return f"{MEDIA_FOLDER_PATH}/photos/users/{user_id}.jpg" \
        if is_photo_exist(user_id=user_id) \
        else f"{MEDIA_FOLDER_PATH}/photos/system/no_image.png"
