import requests
from bs4 import BeautifulSoup, NavigableString
from .models.pydantic_models import Product, KBA_File


class KBAScraper:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "KBA-Scraper/1.0"
        })

    def get(self, url: str) -> requests.Response:
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response

    def discover_files(self, product: Product) -> list[KBA_File]:

        kba_files_list = []

        response = self.get(product.url)

        soup = BeautifulSoup(response.text, "html.parser")

        kba_elements = soup.find_all("a", class_="c-publication")

        for element in kba_elements:
            text = next(child.strip() for child in element.children if isinstance(child, NavigableString) and child.strip())
            download_path = element["href"]

            kba_files_list.append(KBA_File(text=text, download_path=download_path))

        return kba_files_list
