# Netmap v2

Infrastructure and Network Mapping Application.

## Architecture

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL + PostGIS (Dockerized)
- **Frontend**: HTML5 + TailwindCSS + Leaflet (served via FastAPI StaticFiles for now)
- **Infrastructure**: Docker Compose

## Quick Start

1.  Clone the repository.
2.  Ensure Docker and Docker Compose are installed.
3.  Run the application:

    ```bash
    docker-compose up --build
    ```

4.  Access the application at: `http://localhost:8000`
5.  API Documentation: `http://localhost:8000/docs`

## Project Structure

- `/app`: Backend application code
    - `/api`: API route endpoints
    - `/models`: Database models and Pydantic schemas
- `/static`: Frontend assets (HTML, JS, CSS)
- `/scripts`: Utility scripts (e.g., SSH tunnels)

## Theme
Uses Catppuccin Mocha palette.
