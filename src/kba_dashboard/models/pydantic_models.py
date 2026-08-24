from pydantic import BaseModel, HttpUrl
from pathlib import Path

class Product(BaseModel):
    name: str
    url: HttpUrl
    filename_pattern: str

class KBAFile(BaseModel):
    text: str
    download_path: str
    filename: str
    year: int
    month: int
    storage_path: str | None
