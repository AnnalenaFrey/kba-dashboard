from starlette.concurrency import run_in_threadpool

from.scraper import KBAScraper
from .storage import Storage
from .database import DatabaseAdapter
from .models.pydantic_models import Product


async def download_and_save_all(scraper: KBAScraper,
                                storage: Storage,
                                db: DatabaseAdapter,
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
