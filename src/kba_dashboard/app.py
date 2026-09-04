from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from .dependecies import get_database, get_scraper, get_storage
from .config import load_config
from .database import PostgresAdapter
from .storage import LocalStorage
from .scraper import KBAScraper

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load environment variables and config
    load_dotenv()
    config = load_config()

    # Connect to database
    db = PostgresAdapter(connection_string=config["postgres_connection_string"])
    await db.open()
    app.state.db = db

    # Create storage
    app.state.storage = LocalStorage("downloads")

    # Create KBAScraper
    app.state.scraper = KBAScraper()

    yield
    await db.close()


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}
