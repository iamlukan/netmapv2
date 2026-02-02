# Netmap v2

Infrastructure and Network Mapping Application.

## Architecture

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL + PostGIS (Dockerized)
- **Frontend**: HTML5 + TailwindCSS + Leaflet
- **Infrastructure**: Docker Compose + SSH Tunnel

## Quick Start

1.  Clone the repository.
2.  Ensure Docker and Docker Compose are installed.
3.  **SSH Tunnel Config**:
    - Ensure your SSH private key is available at `~/.ssh/id_rsa` (Windows: `%USERPROFILE%\.ssh\id_rsa`).
    - Update `docker-compose.yml` `SSH_HOST` with the jumpbox address if needed.
4.  Run the application:

    ```bash
    docker-compose up --build
    ```

5.  Access:
    - App: `http://localhost:8000`
    - API: `http://localhost:8000/docs`
    - OCS Tunnel: `localhost:5433` (Requires active tunnel)

## Project Structure

- `/app`: Backend application code
    - `/api`: API route endpoints
    - `/models`: Database models (SQLAlchemy + GeoAlchemy2)
- `/static`: Frontend assets
- `/scripts`: Utility scripts

## Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | Local DB Connection String | `postgresql://netmap:netmap_password@netmap-db:5432/netmap` |
| `SSH_HOST` | Tunnel Host Address | *Required* |
| `SSH_USER` | Tunnel User | `admband` |

## Theme
Uses Catppuccin Mocha palette.
