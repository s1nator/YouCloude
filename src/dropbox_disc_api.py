from cloud_interface import Cloud
from functools import partial
import requests
import json
import concurrent.futures
import os


class DropBoxDiskAPI(Cloud):

    def __init__(self, token: str, local_path: str):
        self.token = token
        self._local_path = local_path
        self.path_for_dropbox = ""
        self._url_for_listing_files = "https://api.dropboxapi.com/2/files/list_folder"
        self._url_for_get_file = "https://content.dropboxapi.com/2/files/download"
        self._url_for_post_file = "https://content.dropboxapi.com/2/files/upload"
        self._url_for_make_folder = (
            "https://api.dropboxapi.com/2/files/create_folder_v2"
        )

    def concurrent_upload(self, root, files, path_name) -> None:
        len_path_pathname = len(path_name.split("/"))
        split_path_for_dropbox = root.split("/")[len_path_pathname - 1 :]
        path_for_dropbox = "/".join(split_path_for_dropbox)
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        data = {"path": f"/{path_for_dropbox}", "autorename": True}
        response = requests.post(self._url_for_make_folder, headers=headers, json=data)
        if response.status_code == 200:
            pass
        else:
            raise Exception("Ошибка {response.status_code}{response.text}")
        for file in files:
            self.path_for_dropbox = path_for_dropbox
            self.upload_file(os.path.join(root, file))

    def upload_directory(self, path_name) -> None:
        for root, dirs, files in os.walk(path_name):
            worker = partial(self.concurrent_upload, files=files, path_name=path_name)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(worker, root)

    def download_file(self, path_name) -> None:
        file_name = path_name.split("/")[-1]
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Dropbox-API-Arg": json.dumps({"path": path_name}),
        }

        try:
            if os.path.exists(f"{self._local_path}/{file_name}"):
                number_of_bytes_downloaded = os.path.getsize(
                    f"{self._local_path}/{file_name}"
                )
            else:
                number_of_bytes_downloaded = 0

            if number_of_bytes_downloaded > 0:
                headers["Range"] = f"bytes={number_of_bytes_downloaded}-"

            with requests.post(
                self._url_for_get_file, headers=headers, stream=True
            ) as response:

                if response.status_code == 200:
                    mode_file_entries = "wb"
                elif response.status_code == 206:
                    mode_file_entries = "ab"
                elif response.status_code == 416:
                    return
                else:
                    raise Exception(f"Ошибка скачивания {response.status_code}")

                with open(f"{self._local_path}/{file_name}", mode_file_entries) as file:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            file.write(chunk)

        except (requests.exceptions.RequestException, ConnectionError) as e:
            raise Exception(e)

    def list_files(self, count) -> str:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        data = {"path": "", "recursive": True, "include_media_info": False}

        response = requests.post(
            self._url_for_listing_files, headers=headers, json=data
        )
        listing_files = response.json()
        string_files_and_folders = ""

        if response.status_code == 200:
            for file in listing_files["entries"]:
                name = file["name"]
                path = file["path_display"]
                item_type = file[".tag"]
                if item_type == "folder":
                    string_files_and_folders += f"Folder: {name}, Path: {path}\n"
                elif item_type == "file":
                    string_files_and_folders += f"File: {name}, Path: {path}\n"
        else:
            raise Exception("Ошибка {response.status_code}")

        return string_files_and_folders

    def upload_file(self, path_name) -> None:
        args = {
            "path": f"{self.path_for_dropbox}/{path_name.split('/')[-1]}",
            "mode": "add",
            "autorename": True,
            "mute": False,
            "strict_conflict": False,
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps(args),
        }

        with open(f"{path_name}", "rb") as file:
            response = requests.post(
                self._url_for_post_file, headers=headers, data=file
            )

        if response.status_code == 200:
            pass
        else:
            raise Exception(f"Ошибка загрузки {response.status_code}\n{response.text}")
