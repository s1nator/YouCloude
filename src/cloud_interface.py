from abc import ABC, abstractmethod


class Cloud(ABC):
    _headers: dict

    @abstractmethod
    def upload_directory(self, path_name) -> None:
        pass

    @abstractmethod
    def upload_file(self, path_name: str) -> None:
        pass

    @abstractmethod
    def download_file(self, path_name: str) -> None:
        pass

    @abstractmethod
    def list_files(self, count: int) -> str:
        pass
