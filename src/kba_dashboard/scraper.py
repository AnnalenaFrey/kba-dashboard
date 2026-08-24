import requests
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin, urlparse
import regex as re
from pathlib import Path
from .models.pydantic_models import Product, KBAFile
from .storage import Storage


class KBAScraper:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "KBA-Scraper/1.0"
        })

    def _get(self, url: str) -> requests.Response:
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response

    def discover_files(self, product: Product) -> list[KBAFile]:

        kba_files_list = []

        response = self._get(product.url)

        soup = BeautifulSoup(response.text, "html.parser")

        kba_elements = soup.find_all("a", class_="c-publication")

        for element in kba_elements:
            match = re.match(product.filename_pattern, element["href"])
            if not match:
                continue

            text = next(child.strip() for child in element.children if isinstance(child, NavigableString) and child.strip())
            download_path = str(element["href"])
            filename = str(Path(urlparse(download_path).path).name)
            year = int(match.group(1))
            month = int(match.group(2))

            kba_files_list.append(KBAFile(text=text, download_path=download_path, filename=filename, year=year, month=month, storage_path=None))

        return kba_files_list

    def download_file(self, base_url: str, kba_file: str, storage: Storage) -> None:

        download_url = urljoin(base_url, kba_file.download_path)
        response = self._get(download_url)
        storage_location = str(storage.save(kba_file.filename, response))

        return storage_location

