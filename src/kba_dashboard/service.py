from starlette.concurrency import run_in_threadpool

from.scraper import KBAScraper
from .storage import Storage
from .database import PostgresAdapter
from .models.pydantic_models import Product, KBAFile
from .processing import read_excel


async def download_and_save_all(scraper: KBAScraper,
                                storage: Storage,
                                db: PostgresAdapter,
                                product: Product,
                                base_url: str,
                                status: dict):

    status["state"] = "running"
    status["error"] = None

    try:
        files = await run_in_threadpool(scraper.discover_files, product=product)
        print(f"Discovered files: {files}")
        saved = 0
        for file in files:
            if await db.check_if_file_exists(download_path=file.download_path):
                continue
            file.storage_location = await run_in_threadpool(scraper.download_file, base_url=base_url, kba_file=file, storage=storage)
            await db.save_raw_file(file)
            saved += 1
        status["state"] = "done"
        status["result"] = {"saved": saved, "total_discovered": len(files)}
    except Exception as e:
        status["state"] = "failed"
        status["error"] = str(e)

async def process_all_files(db: PostgresAdapter, status: dict):

    status["state"] = "running"
    status["error"] = "None"

    try: 
        raw_files = await db.get_raw_files()
        processed = 0

        for row in raw_files:
            raw_file = KBAFile(**row)

            records = await run_in_threadpool(read_excel, raw_file)
            await db.save_processed_records(records)
            processed += 1

        status["state"] = "done"
        status["result"] = {"processed": processed, "out of": len(raw_files)}

    except Exception as e:
        status["state"] = "failed"
        status["error"] = str(e)