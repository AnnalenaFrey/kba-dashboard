from fastapi import Request

from .scraper import KBAScraper
from .storage import LocalStorage
from .database import PostgresAdapter

def get_database(request: Request) -> PostgresAdapter:
    return request.app.state.db

def get_storage(request: Request) -> LocalStorage:
    return request.app.state.storage

def get_scraper(request: Request) -> KBAScraper:
    return request.app.state.scraper
