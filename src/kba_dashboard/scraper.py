import requests
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin
import regex as re
from .models.pydantic_models import Product, KBA_File


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
            if re.search(product.filename_pattern, element["href"]):
                text = next(child.strip() for child in element.children if isinstance(child, NavigableString) and child.strip())
                download_path = element["href"]
                kba_files_list.append(KBA_File(text=text, download_path=download_path))
            else:
                pass

        return kba_files_list

    def download_files(self, base_url: str, kba_files_list: list[KBA_File]) -> None:

        for element in kba_files_list:
            download_url = urljoin(base_url, element.download_path)

            print(download_url)
