from .scraper import KBAScraper
from .config import fz11, BASE_URL, connection_string
from .storage import LocalStorage
from pathlib import Path
from .models.pydantic_models import KBAFile
from .database import PostgresAdapter



def main() -> None:
    client = KBAScraper()
    storage = LocalStorage(Path("downloads"))
    db = PostgresAdapter(connection_string=connection_string)
    db.open()

    files = client.discover_files(fz11)

    for file in files:
        file.storage_path = client.download_file(BASE_URL, file, storage)
        db.save_raw_document(file)

    db.close()


main()