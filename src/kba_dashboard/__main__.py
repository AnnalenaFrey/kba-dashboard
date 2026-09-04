from .scraper import KBAScraper
from .config import load_config
from .storage import LocalStorage
from pathlib import Path
from .database import PostgresAdapter
from dotenv import load_dotenv
from .models.pydantic_models import Product, KBAFile


def main() -> None:
    load_dotenv()
    config = load_config()

    client = KBAScraper()
    storage = LocalStorage("downloads")
    db = PostgresAdapter(connection_string=config["postgres_connection_string"])

    db.open()

    files = client.discover_files(Product(**config["products"]["fz11"]))

    for file in files:
        if db.check_if_file_exists(download_path=file.download_path):
            print(f"File '{file.filename}' already downloaded, therefore skipping ...")
            continue

        file.storage_location = client.download_file(config["base_url"], file, storage)
        raw_saved = db.save_raw_file(file)
        file_saved = KBAFile(**raw_saved)
        print(f"Successfully downloaded file '{file_saved.filename}' with ID '{file_saved.id}' at '{file_saved.storage_location}'")

    db.close()

main()