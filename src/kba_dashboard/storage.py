from abc import ABC, abstractmethod
from pathlib import Path
import requests

class Storage(ABC):

    @abstractmethod
    def save(self, file: str):
        pass

class LocalStorage(Storage):
    def __init__(self, root: Path):
        self.root = root

    def save(self, file: str, response: requests.Response) -> None:
        path = self.root / file

        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    