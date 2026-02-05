# Netmap v2 - Project Manifesto 🗺️

Netmap is an advanced Indoor Mapping and Infrastructure Management system designed for high aesthetics and robust data handling. It integrates physically mapped assets with OCS Inventory data via secure tunnels.

## 🏗️ Architecture

```mermaid
graph TD
    User["User / Browser"] -->|HTTP 8000| App["FastAPI App"]
    App -->|SQLAlchemy| DB["PostgreSQL + PostGIS"]
    App -->|SSH Tunnel :3306| OCS["OCS Inventory DB (Remote)"]
    
    subgraph Docker Network
        App
        DB
        Tunnel["SSH Tunnel Container"]
    end
    
    Tunnel -->|SSH| Jumpbox["Gateway Server"]
    Jumpbox -->|MySQL| OCS
```

**Stack:**
- **Backend:** Python 3.12 (uv), FastAPI, SQLAlchemy (Async).
- **Frontend:** Vanilla JS, Leaflet.js, TailwindCSS (Catppuccin Mocha Theme).
- **Database:** PostgreSQL 16 with PostGIS.
- **Infrastructure:** Docker Compose (All services containerized).

---

## 🚀 Deployment Guide (Ubuntu Production)

Follow these steps to deploy Netmap v2 on a fresh Ubuntu server.

### 1. Prerequisites
- **Ubuntu 20.04+** or **Debian 11+**
- **Docker** & **Docker Compose** installed.
- **SSH Private Key** (`id_ed25519` or `id_rsa`) authorizing access to the OCS Gateway.

### 2. Installation Steps

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/iamlukan/netmapv2.git
    cd netmapv2
    ```

2.  **Setup SSH Credentials**:
    Place your private key in a secure folder (e.g., `keys/`).
    ```bash
    mkdir keys
    cp /path/to/your/id_ed25519 ./keys/
    chmod 600 ./keys/id_ed25519
    ```

3.  **Environment Configuration**:
    Create a `.env` file based on the example.
    ```bash
    cp .env.example .env
    nano .env
    ```
    **Critical Variables to Edit:**
    ```ini
    # Database (Internal Netmap DB)
    POSTGRES_USER=netmap
    POSTGRES_PASSWORD=secure_password_here
    POSTGRES_DB=netmap
    DATABASE_URL=postgresql://netmap:secure_password_here@netmap-db:5432/netmap

    # Security
    SECRET_KEY=generate_a_random_secure_string_here

    # OCS Inventory Tunnel (Remote Access)
    SSH_HOST=10.0.0.1          # Gateway IP
    SSH_USER=ubuntu            # Gateway User
    SSH_KEY_PATH=/root/ssh/id_ed25519 # Path INSIDE container (Keep as is)
    
    # OCS Database Config (Remote MySQL credentials)
    OCS_DB_HOST=netmap-tunnel  # Hostname alias from Docker Compose
    OCS_DB_PORT=3306           # Local Tunnel Port
    OCS_DB_USER=ocs_reader
    OCS_DB_PASS=ocs_reader_pass
    OCS_DB_NAME=ocsweb
    ```

4.  **Important**: Update `docker-compose.yml` volume for SSH Key.
    Ensure the `netmap-tunnel` service mounts your local key to the container path expected by `.env`.
    
    *If your local key is in `./keys/id_ed25519`:*
    ```yaml
    # docker-compose.yml
    netmap-tunnel:
      volumes:
        - ./keys/id_ed25519:/root/ssh/id_ed25519:ro
    ```

### 3. Build & Run
 
Choose the mode that fits your needs:

#### A. Standard Mode (App + DB)
Ideal for local testing or when OCS access is not required.
```bash
docker compose up -d --build
```

#### B. Full Mode (App + DB + Tunnel)
Required for production or when you need real-time data from OCS Inventory.
```bash
docker compose --profile tunnel up -d --build
```
    
**That's it!** In both modes, the system will automatically:
- Wait for the database to be ready.
- Create the tables.
- Create the default Admin user (`admin` / `admin123` or `${ADMIN_PASSWORD}`).
- Start the application.

### 4. Verification

Check if everything is running:
```bash
docker compose logs -f
```
You should see: `Admin user created: admin / admin123` (on first run).

### 5. Access & Updates

- **Access:** Open `http://YOUR_SERVER_IP:8000`
- **Logs:** `docker-compose logs -f`
- **Update:**
    ```bash
    git pull
    # Use --profile tunnel if running in Full Mode
    docker compose --profile tunnel up -d --build
    ```

---

## 🔧 Maintenance

### Backup Database
```bash
docker exec -t netmap-db pg_dumpall -c -U netmap > dump_$(date +%Y-%m-%d).sql
```

### Restore Database
```bash
cat dump_file.sql | docker exec -i netmap-db psql -U netmap
```

---

## 📡 API Endpoints

- `GET /api/nodes?floor_id=X`: List nodes for specific floor.
- `GET /api/search?q=XYZ`: Global search (auto-layer switching).
- `GET /api/export/excel`: Export filtered inventory data.
- `GET /api/ocs/machine/{name}`: Get real-time OCS hardware info.

---

## 🎨 Design System

**Colors (Catppuccin Mocha):**
- Base: `#1e1e2e` (Backgrounds)
- Text: `#cdd6f4` (Content)
- Blue: `#89b4fa` (Actions/Equipments)
- Green: `#a6e3a1` (Success/Computers)
- Red: `#f38ba8` (Errors/Missing)
- Mauve: `#cba6f7` (Ramals/Admin)

**UI Components:**
Wait for `L.control.layers` to toggle visibility of:
Computadores | Ramais | Pontos | Equipamentos | Textos
