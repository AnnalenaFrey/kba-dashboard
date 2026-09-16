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

class FZ11Record(BaseModel):
    id: UUID | None = None
    segment: str
    model_series: str
    brand: str
    model: str | None
    car_registrations: int
    commercial_share: float | None
    year: int
    month: int
    raw_file_id: UUID

class QuarterPeriod(BaseModel):
    year: int
    quarter: int
    total: int

class QuarterComparison(BaseModel):
    period1: QuarterPeriod
    period2: QuarterPeriod
    absolute_diff: int
    percentage_diff: float | None
