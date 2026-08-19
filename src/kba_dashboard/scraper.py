import requests
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin, urlparse
import regex as re
from pathlib import Path
from .models.pydantic_models import Product, KBA_File
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

    def discover_files(self, product: Product) -> list[KBA_File]:

        kba_files_list = []

        response = self._get(product.url)

        soup = BeautifulSoup(response.text, "html.parser")

        kba_elements = soup.find_all("a", class_="c-publication")

        for element in kba_elements:
            if not re.match(product.filename_pattern, element["href"]):
                continue

            text = next(child.strip() for child in element.children if isinstance(child, NavigableString) and child.strip())
            download_path = element["href"]
            filename = Path(urlparse(download_path).path).name

            kba_files_list.append(KBA_File(text=text, download_path=download_path, filename=filename))

        return kba_files_list

    def download_files(self, base_url: str, kba_files_list: list[KBA_File], storage: Storage) -> None:

        for element in kba_files_list:
            download_url = urljoin(base_url, element.download_path)

            response = self._get(download_url)

            storage.save(element.filename, response)

