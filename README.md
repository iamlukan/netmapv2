# Netmap v2

Infrastructure and Network Mapping Application.

## Architecture

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL + PostGIS (Dockerized)
- **Frontend**: HTML5 + TailwindCSS + Leaflet
- **Infrastructure**: Docker Compose + SSH Tunnel

## OCS Integration & SSH Tunneling

Netmap integrates with **OCS Inventory** to display real-time machine data. This connection often requires an SSH Tunnel to reach the database securely.

### Prerequisites

1.  **SSH Key**: You need an SSH Private Key (`id_ed25519` or `id_rsa`) authorized on the Gateway.
2.  **Environment Variables**:
    - `SSH_HOST`: IP of the Jumpbox/Gateway.
    - `SSH_USER`: SSH Username (e.g., `user`).
    - `SSH_KEY_PATH`: Local path to your private key.
    - `OCS_DATABASE_URL`: Connection string for the OCS MySQL database.

### Setup Guide

1.  **Place your Key**:
    Copy your private key to a known location, e.g., `%USERPROFILE%\.ssh\id_ed25519`.

2.  **Configure .env**:
    ```ini
    SSH_HOST=192.168.1.100
    SSH_USER=user
    SSH_KEY_PATH=C:/Users/YourUser/.ssh/id_ed25519
    # The tunnel maps remote 3306 (MySQL) to container 5433 (or similar)
    OCS_DATABASE_URL=mysql+pymysql://ocs_user:ocs_password@netmap-tunnel:5432/ocsweb
    ```
    *Note: The `netmap-tunnel` service in docker-compose handles the port forwarding.*

3.  **Start Services**:
    ```bash
    docker-compose up -d --build
    ```

4.  **Verify Connection**:
    - Check the tunnel logs: `docker logs netmap-tunnel`.
    - Check the App status via API: `GET /api/test-db` or check the status badge in the UI header.

## Quick Start

1.  Clone the repository.
2.  Ensure Docker and Docker Compose are installed.
3.  **Configuration**: Create `.env` (see above).
4.  Run: `docker-compose up --build`
5.  Access: `http://localhost:8000`

## Project Structure

- `/app`: Backend application code
    - `/api`: API route endpoints
    - `/models`: Database models
    - `/services`: Business logic and external integrations
- `/static`: Frontend assets
- `/scripts`: Utility scripts

## Theme
Uses Catppuccin Mocha palette.
