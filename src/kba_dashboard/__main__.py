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
    print(config)


    client = KBAScraper()
    storage = LocalStorage(Path("downloads"))
    db = PostgresAdapter(connection_string=config["postgres_connection_string"])

    db.open()

    files = client.discover_files(Product(**config["products"]["fz11"]))

    for file in files:
        file.storage_path = client.download_file(config["base_url"], file, storage)
        db.save_raw_document(file)

    db.close()

main()