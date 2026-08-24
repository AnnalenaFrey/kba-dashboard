from .scraper import KBAScraper
from .config import fz11, BASE_URL
from .storage import LocalStorage
from pathlib import Path



def main() -> None:
    client = KBAScraper()
    storage = LocalStorage(Path("downloads"))
    files = client.discover_files(fz11)

    print(files)

    for file in files:
        client.download_file(BASE_URL, file, storage)

main()