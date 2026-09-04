from abc import ABC, abstractmethod
from pathlib import Path
import requests

class Storage(ABC):

    @abstractmethod
    def save(self, file: str, response: requests.Response):
        pass

    @abstractmethod
    def delete(self, file: str):
        pass

class LocalStorage(Storage):
    def __init__(self, root: str):
        self.root = Path(root)

    def save(self, file: str, response: requests.Response) -> Path:
        path = self.root / file

        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return path

    def delete(self, file: str):
        file_to_remove_path = Path(file)
        try:
            file_to_remove_path.unlink()
            print(f"Successfully deleted file '{file}'")
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{file}' not found")
                    