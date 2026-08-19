from pydantic import BaseModel, HttpUrl
from pathlib import Path

class Product(BaseModel):
    name: str
    url: HttpUrl
    filename_pattern: str

class KBA_File(BaseModel):
    text: str
    download_path: str
    filename: str
