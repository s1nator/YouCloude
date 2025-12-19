import sys
from yandex_disc_api import YandexDiskApi
from refresh_script import get_dropbox_token
from dropbox_disc_api import DropBoxDiskAPI
from config import (
    token_for_yandex,
    path_for_files_yandex,
    path_for_download_from_yandex_disc,
    limit_files_for_listing,
    local_path_for_dropbox,
)


def commands(arguments, cloud) -> None:
    if arguments[1] == "-l":
        print(cloud.list_files(limit_files_for_listing))
    if arguments[1] == "-g":
        cloud.download_file(arguments[2])
    if arguments[1] == "-p":
        cloud.upload_file(arguments[2])
    if arguments[1] == "-pc":
        cloud.upload_directory(arguments[2])


def main() -> None:
    arguments = sys.argv[1:]

    if arguments[0] == "-y" or arguments[0] == "--yandex":
        cloud = YandexDiskApi(
            token_for_yandex,
            path_for_download_from_yandex_disc,
            path_for_files_yandex,
            local_path_for_dropbox,
        )
        commands(arguments, cloud)

    if arguments[0] == "-d" or arguments[0] == "--dropbox":
        access_token = get_dropbox_token()
        dropbox = DropBoxDiskAPI(access_token, local_path_for_dropbox)
        commands(arguments, dropbox)


if __name__ == "__main__":
    main()
