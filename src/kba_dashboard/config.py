from .models.pydantic_models import Product
import regex

fz11 = Product(
    name = "fz11",
    url = "https://www.kba.de/DE/Statistik/Produktkatalog/produkte/Fahrzeuge/fz11/fz11_gentab.html",
    filename_pattern=r".*fz11_(\d{4})_(\d{2}).*(?:xlsx|xls).*" 
)

BASE_URL = "https://www.kba.de"

connection_string = "postgresql://postgres:password@localhost:5432"