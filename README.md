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
3.  **Configuration**:
    - Create a `.env` file based on `.env.example`.
    - Set `SSH_HOST` to your SSH Gateway IP.
    - Set `SSH_USER` (Default: `admband`).
    - Ensure your SSH private key is available at `%USERPROFILE%\.ssh\id_rsa`.
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

Check `.env.example` for reference.

## Troubleshooting

### SSH Tunnel Issues
- Ensure `id_rsa` has correct permissions (though on Windows Docker mounts this can be tricky, the Alpine container usually handles it if mounted read-only).
- Check logs: `docker logs netmap-tunnel`.

## Theme
Uses Catppuccin Mocha palette.
