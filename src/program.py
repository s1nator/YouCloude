from dropbox_disc_api import DropBoxDiskAPI
from yandex_disc_api import YandexDiskApi
from refresh_script import get_dropbox_token

import config

token = get_dropbox_token()
drop = DropBoxDiskAPI(token,
                   "data/downloading_files")


yandex = YandexDiskApi(config.token_for_yandex,
                       "disk:/",
                       "disk:/python_task",
                       "data/downloading_files")
print(drop.list_files(15))
print("\n\n\n")
print(yandex.list_files(15))