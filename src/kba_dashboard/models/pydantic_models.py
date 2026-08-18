from pydantic import BaseModel, HttpUrl

class Product(BaseModel):
    name: str
    url: HttpUrl
    filename_pattern: str

class KBA_File(BaseModel):
    text: str
    download_path: str
