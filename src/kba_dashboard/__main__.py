from .scraper import KBAScraper
from .config import fz11, BASE_URL



def main() -> None:
    client = KBAScraper()
    files = client.discover_files(fz11)
    client.download_files(BASE_URL, files)

main()