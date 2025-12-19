import yaml
import os


full_path = os.getcwd()
full_path = full_path.split("/")[:-1]
full_path = "/".join(full_path)


with open(f"{full_path}/configuration.yaml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)


token_for_yandex = cfg["database"]["token_for_yandex_disk"]
path_for_files_yandex = cfg["database"]["path_for_files_yandex"]
path_for_download_from_yandex_disc = cfg["database"][
    "path_for_download_from_yandex_disc"
]
limit_files_for_listing = cfg["database"]["limit_files_for_listing"]
refresh_token_for_dropbox = cfg["database"]["refresh_token_for_dropbox_disk"]
app_key_dropbox = cfg["database"]["app_key_dropbox"]
app_secret_dropbox = cfg["database"]["app_secret_dropbox"]
access_token_dropbox = cfg["database"]["access_token_for_dropbox"]
local_path_for_dropbox = cfg["database"]["local_path_for_dropbox"]
