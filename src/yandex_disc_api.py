from cloud_interface import Cloud
import requests
import os
import concurrent.futures
from functools import partial
import json


class YandexDiskApi(Cloud):

    def __init__(
        self,
        token: str,
        path_for_download_from_yandex_disc: str,
        path_for_files_yandex: str,
        folder_for_download: str,
    ):
        self._headers = {"Authorization": f"OAuth {token}"}
        self._folder_for_download = folder_for_download
        self._path_for_yandex_disk = ""
        self._path_for_download_from_yandex_disc = path_for_download_from_yandex_disc
        self._path_for_files_yandex = path_for_files_yandex
        self._yandex_disk_url_start = "https://cloud-api.yandex.net/v1/disk/resources"

    def concurrent_upload(self, root, files, path_name) -> None:
        len_path_pathname = len(path_name.split("/"))
        split_path_for_yandex_disk = root.split("/")[len_path_pathname - 1 :]
        path_for_yandex_disk = "/".join(split_path_for_yandex_disk)
        headers = self._headers
        params = {"path": f"{self._path_for_files_yandex}/{path_for_yandex_disk}"}

        response = requests.put(
            self._yandex_disk_url_start, headers=headers, params=params
        )
        if response.status_code == 200:
            pass
        elif response.status_code == 201:
            pass
        elif response.status_code == 409:
            pass
        else:
            raise Exception(f"Ошибка {response.status_code}{response.text}")
        for file in files:
            self._path_for_yandex_disk = path_for_yandex_disk
            self.upload_file(os.path.join(root, file))

    def upload_directory(self, path_name: str) -> None:
        for root, dirs, files in os.walk(path_name):
            worker = partial(self.concurrent_upload, files=files, path_name=path_name)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(worker, root)

    def upload_file(self, path_name: str) -> None:
        name_file = path_name.split("/")[-1]
        url = (
            f"{self._yandex_disk_url_start}/upload?path="
            f"{self._path_for_files_yandex}/{self._path_for_yandex_disk}/{name_file}&[overwrite=False]&[fields=name,_embedded.items.path]"
        )
        response_get = requests.get(url, headers=self._headers)
        url = response_get.json()["href"]
        try:
            with open(path_name, "rb") as file:
                requests.put(url, data=file, headers=self._headers)

        except Exception as e:
            raise Exception(f"Ошибка Вы ввели неверный путь: {e}")

    def download_file(self, file_name: str) -> None:
        try:
            url = (
                f"{self._yandex_disk_url_start}/download?path="
                f"{self._path_for_download_from_yandex_disc}{file_name}&[fields=name,_embedded.items.path]"
            )
            if os.path.exists(f"{self._folder_for_download}/{file_name}"):
                number_of_bytes_downloaded = os.path.getsize(
                    f"{self._folder_for_download}/{file_name}"
                )
            else:
                number_of_bytes_downloaded = 0

            if number_of_bytes_downloaded > 0:
                self._headers["Range"] = f"bytes={number_of_bytes_downloaded}-"

            with requests.get(url, headers=self._headers) as response_get_link:
                try:
                    href = response_get_link.json()["href"]
                    response = requests.get(href)
                    file_name = file_name.split("/")[-1]

                    with open(f"{self._folder_for_download}/{file_name}", "wb") as file:
                        for chunk in response.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                file.write(chunk)

                except Exception as e:
                    raise Exception(f"Ошибка Такого файла не существует: {e}")
        except Exception as e:
            raise Exception(f"Ошибка {e}")

    def list_files(self, count: int) -> str:
        url_for_files = (
            f"{self._yandex_disk_url_start}/files"
            f"?[limit={count}]"
            f"&[media_type=audio,video,backup, book,compressed,data,development,diskimage,document,encoded,executable,flash, font, image,settings, spreadsheet, text, unknown,web]"
            f"&[offset=0]"
            f"&[fields=name,_embedded.items.path]"
            f"&[preview_size=M]"
            f"&[preview_crop=true]"
        )
        response_get_link = requests.get(url_for_files, headers=self._headers)
        data = json.loads(response_get_link.text)
        string_with_files = ""
        for item in data.get("items", []):
            path = item.get("path", "")
            string_with_files += f"File: {path}\n"

        return string_with_files
