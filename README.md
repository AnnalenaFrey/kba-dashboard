# KBA Dashboard

**Web-Crawler and Dashboard for KBA Analytics (Kraftfahrt-Bundesamt)**

This project aims to demonstrate different analytics based on data from the KBA.

## How to run

### Prerequisites
 * Ensure that Docker is installed
 * Ensure that uv is installed
 * Clone the repository via ``git clone git@github.com:AnnalenaFrey/kba-dashboard.git``
 * Run ``uv sync`` to recreate the python environment

### Run
 * Start the Docker container via ``docker compose up``
 * Run the application in dev environment via ``uv run python -m fastapi dev``
 
Open browser at ``127.0.0.1/docs`` to see the OpenAPI documentation and try it out

Check out the database via pgAdmin at ``localhost:8080``

