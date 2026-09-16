from fastapi import FastAPI, BackgroundTasks, Depends, Query, HTTPException
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from typing import Annotated


from .dependecies import get_database, get_scraper, get_storage, get_scrape_status, get_config, get_product, get_base_url, get_processing_status
from .config import load_config
from .database import PostgresAdapter
from .storage import LocalStorage
from .scraper import KBAScraper
from .service import download_and_save_all, process_all_files
from .models.pydantic_models import QuarterPeriod, QuarterComparison

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load environment variables and config
    load_dotenv()
    config = get_config()

    # Connect to database
    db = PostgresAdapter(connection_string=config["postgres_connection_string"])
    await db.open()
    app.state.db = db

    # Create storage
    app.state.storage = LocalStorage("downloads")

    # Create KBAScraper
    app.state.scraper = KBAScraper()
    app.state.scrape_status = {"state": "idle", "result": None, "error": None}

    app.state.processing_status = {"state": "idle", "result": None, "error": None}

    yield
    await db.close()


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/files/{product_name}")
async def download_all_files(background_tasks: BackgroundTasks, 
                             db = Depends(get_database),
                             storage = Depends(get_storage),
                             scraper = Depends(get_scraper),
                             status: dict = Depends(get_scrape_status),
                             product = Depends(get_product),
                             base_url: str = Depends(get_base_url)
                             ):
    background_tasks.add_task(download_and_save_all, 
                              scraper=scraper,
                              storage=storage,
                              db=db,
                              product=product,
                              base_url=base_url,
                              status=status)
    return {"status": "Started scraping process..."}

@app.get("/files/status")
async def download_status(status:dict = Depends(get_scrape_status)):
    return status

@app.post("/process")
async def process_files(background_tasks: BackgroundTasks,
                        db = Depends(get_database),
                        status: dict = Depends(get_processing_status)
                        ):
    background_tasks.add_task(process_all_files, db, status)
    return {"status": "Started processing files..."}

@app.get("/process/status")
async def process_status(status:dict = Depends(get_processing_status)):
    return status

@app.get("/analytics/quarterly")
async def quaterly_comparison(year1: Annotated[int, Query(description="First year you want to compare")], 
                              quarter1: Annotated[int, Query(description="First quater you want to compare")], 
                              year2: Annotated[int, Query(description="Second year you want to compare")], 
                              quarter2: Annotated[int, Query(description="Second quarter you want to compare")],
                              db: PostgresAdapter = Depends(get_database)):
    total_period1 = await db.get_quaterly_total(year=year1, quarter=quarter1)
    total_period2 = await db.get_quaterly_total(year=year2, quarter=quarter2)

    if total_period1 == None or total_period2 == None:
        raise HTTPException(status_code=404, detail="No data found for one or more requested periods.")

    diff = total_period2 - total_period1
    pct = (diff / total_period1) * 100 if total_period1 > 0 else None
    return QuarterComparison(
        period1=QuarterPeriod(year=year1, quarter=quarter1, total=total_period1),
        period2 = QuarterPeriod(year=year2, quarter=quarter2, total=total_period2),
        absolute_diff=diff,
        percentage_diff = pct
    )


    