from .scraper import KBAScraper
from .config import load_config
from .storage import LocalStorage
from pathlib import Path
from .database import PostgresAdapter
from dotenv import load_dotenv
from .models.pydantic_models import Product


def main() -> None:
    load_dotenv()
    config = load_config()

    client = KBAScraper()
    storage = LocalStorage(Path("downloads"))
    db = PostgresAdapter(connection_string=config["postgres_connection_string"])

    db.open()

    files = client.discover_files(Product(**config["products"]["fz11"]))

    for file in files:
        if db.check_if_file_exists(download_path=file.download_path):
            print(f"File '{file.filename}' already downloaded, therefore skipping ...")
            continue

        file.storage_path = client.download_file(config["base_url"], file, storage)
        db.save_raw_document(file)
        print(f"Successfully downloaded file {file.filename} at {file.storage_path}")

    db.close()

main()