from kba_dashboard.models.pydantic_models import Product, KBAFile
from kba_dashboard.scraper import KBAScraper
from kba_dashboard.storage import LocalStorage


class MockResponse:
    def __init__(self, text):
        self.text = text

class MockDownload:
    def iter_content(self, chunk_size):
        return [b"fake file content"]


def test_discover_files_correct_file(monkeypatch):

    scraper = KBAScraper()

    product = Product(
        name="fz11",
        url="https://example.com",
        filename_pattern=r".*fz11_(\d{4})_(\d{2}).*(?:xlsx|xls).*"
    )

    test_html = "<a class='c-publication' href='fz11_2026_08.xlsx'>Fz 11 August 2026</a>"

    monkeypatch.setattr(scraper, "_get", lambda url: MockResponse(test_html))
    
    result = scraper.discover_files(product=product)

    assert len(result) == 1
    assert result[0].year == 2026
    assert result[0].month == 8
    assert result[0].filename == "fz11_2026_08.xlsx"

def test_discover_files_incorrect_file(monkeypatch):
    
    scraper = KBAScraper()
    
    product = Product(
        name="fz11",
        url="https://example.com",
        filename_pattern=r".*fz11_(\d{4})_(\d{2}).*(?:xlsx|xls).*"
    )

    test_html = "<a class='c-publication' href='fz11_august_2026.xlsx'>Fz 11 August 2026</a>"

    monkeypatch.setattr(scraper, "_get", lambda url: MockResponse(test_html))
        
    result = scraper.discover_files(product=product)

    assert len(result) == 0

def test_download_file(monkeypatch, tmp_path):

    scraper = KBAScraper()
    base_url = "https://example.com"
    storage= LocalStorage(tmp_path)
    kba_file = KBAFile(
        id= None,
        text="FZ11 August 2026",
        download_path="",
        filename="fz11_2026_08.xlsx",
        year=2026,
        month=8,
    )

    monkeypatch.setattr(scraper, "_get", lambda url: MockDownload())
    result = scraper.download_file(base_url, kba_file, storage)

    saved_path = tmp_path / "fz11_2026_08.xlsx"
    assert saved_path.exists()
    assert saved_path.read_bytes() == b"fake file content"
    assert result == str(saved_path)

