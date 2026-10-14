# KBA Dashboard

**Web-Crawler and Dashboard for KBA Analytics (Kraftfahrt-Bundesamt)**

A dashboard that scrapes, stores, processes, analyzes and forecasts German vehicle registration statistics from the Kraftfahrt-Bundesamt (KBA)

## Architecture 
* **Backend**: Python + FastAPI; PostgreSQL via psycopg `AsyncConnectionPool`, pytest for testing
    * **Scraping**: Process can be found in `scraper.py`, using requests and BeautifulSoup against the KBA website
    * **Processing**: Processing of the raw files is done in `processing.py`. Here, the downloaded Excel reports are parsed into structured records.
    * **Orchestration**: Background task function (scrape, process, forecast) are in `service.py`, triggered via FastAPI routes in `app.py`
    * **Forecasting**: All logic can be found in `forecasting/`. A working prophet model (total car registrations only) plus a PyTorch model that is a work in progress
* **Frontend**: React + Vite + TypeScript, TanStack Query for data fetching, Recharts for the time-series chart. Functional, not yet styled
* **Package managers**: `uv`(backend), `pnpm`(frontend)

## Current State
* **Scraping & Storage**: downloads KBA FZ 11 monthly registration reports and stores them locally, tracked in PostgreSQL
* **Processing**: parse the Excel reports into structures records (segment, brand, model, total registrations per month)
* **Analytics API**: REST API with quarterly comparisons, a brand/segment filterable time series, and lists of available brands/segments
* **Forecasting**: a prophet model forecasts future registrations which should later be used as a fallback. A pytorch model is still wip
* **Frontend**: a React dashboard with brand/segment filters and a time-series chart. Functional but needs visual polishing
* **Tests**: a pytest suite is just getting started

## How to run

### Prerequisites
 * Ensure that Docker is installed
 * Ensure that uv is installed
 * Ensure that pnpm is installed
 * Clone the repository via `git clone git@github.com:AnnalenaFrey/kba-dashboard.git`
 * Run `uv sync` to recreate the python environment

### Setup
* Create a .env file at the repo root with
`PGPASSWORD="password"`

### Run
 * Start the Docker container via `docker compose up`
 * **Backend**: run the backend in dev environment via `uv run python -m fastapi dev`
 * **Frontend**: run the frontend in dev environment with `pnpm run dev`
 * **Tests**: run the test suite with `uv run pytest`
 
Open browser at `127.0.0.1/docs` to see the OpenAPI documentation and try it out

Check out the database via pgAdmin at `localhost:8080`

The frontend can be accessed at `localhost:5173/`

