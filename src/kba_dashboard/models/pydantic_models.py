from pydantic import BaseModel, HttpUrl
from uuid import UUID

class Product(BaseModel):
    name: str
    url: HttpUrl
    filename_pattern: str

class KBAFile(BaseModel):
    id: UUID | None
    text: str
    download_path: str
    filename: str
    year: int
    month: int
    storage_path: str | None
