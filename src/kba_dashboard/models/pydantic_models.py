from pydantic import BaseModel, HttpUrl
from uuid import UUID
from datetime import datetime

class Product(BaseModel):
    name: str
    url: HttpUrl
    filename_pattern: str

class KBAFile(BaseModel):
    id: UUID | None = None
    text: str
    download_path: str
    filename: str
    year: int
    month: int
    storage_location: str | None = None
    downloaded_at: datetime | None = None
