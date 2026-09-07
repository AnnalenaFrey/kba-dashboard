from fastapi import FastAPI, BackgroundTasks, Depends
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from .dependecies import get_database, get_scraper, get_storage, get_scrape_status, get_config, get_product, get_base_url
from .config import load_config
from .database import PostgresAdapter
from .storage import LocalStorage
from .scraper import KBAScraper
from .service import download_and_save_all

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load environment variables and config
    load_dotenv()
    config = get_config()

    # Connect to database
    db = PostgresAdapter(connection_string=config["postgres_connection_string"])
    await db.open()
    app.state.db = db

    # Create storage
    app.state.storage = LocalStorage("downloads")

    # Create KBAScraper
    app.state.scraper = KBAScraper()
    app.state.scrape_status = {"state": "idle", "result": None, "error": None}

    yield
    await db.close()


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/files/{product_name}")
async def download_all_files(background_tasks: BackgroundTasks, 
                             db = Depends(get_database),
                             storage = Depends(get_storage),
                             scraper = Depends(get_scraper),
                             status: dict = Depends(get_scrape_status),
                             product = Depends(get_product),
                             base_url: str = Depends(get_base_url)
                             ):
    background_tasks.add_task(download_and_save_all, 
                              scraper=scraper,
                              storage=storage,
                              db=db,
                              product=product,
                              base_url=base_url,
                              status=status)
    return {"status": "Started scraping process"}