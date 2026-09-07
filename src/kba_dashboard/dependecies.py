from fastapi import Request, Depends, HTTPException
from functools import lru_cache

from .scraper import KBAScraper
from .storage import LocalStorage
from .database import PostgresAdapter
from .config import load_config
from .models.pydantic_models import Product

def get_database(request: Request) -> PostgresAdapter:
    return request.app.state.db

def get_storage(request: Request) -> LocalStorage:
    return request.app.state.storage

def get_scraper(request: Request) -> KBAScraper:
    return request.app.state.scraper

def get_scrape_status(request: Request)-> dict:
    return request.app.state.scrape_status

@lru_cache
def get_config() -> dict:
    return load_config()

def get_product(product_name: str, config: dict = Depends(get_config)) -> Product:
    products = config["products"]
    if product_name not in products:
        raise HTTPException(status_code=404, detail=f"Unknown product '{product_name}'")

    return Product(**products[product_name])

def get_base_url(config: dict = Depends(get_config))-> str:
    return config["base_url"]
