from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="Netmap v2")

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

from app.api import nodes, diagnostics, floors, ocs, audit

app.include_router(nodes.router, prefix="/api")
app.include_router(diagnostics.router, prefix="/api")
app.include_router(floors.router, prefix="/api")
app.include_router(ocs.router, prefix="/api")
app.include_router(audit.router, prefix="/api")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
