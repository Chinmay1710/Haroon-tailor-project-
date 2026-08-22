import os
import uvicorn
import logging
from threading import Thread
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.worker_service import worker_service
from app.config import ASSETS_DIR

logger = logging.getLogger(__name__)

app = FastAPI(title="Haroon Tailor Worker Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# We will serve mobile web assets from app/assets/mobile
mobile_assets_dir = os.path.join(ASSETS_DIR, "mobile")
os.makedirs(mobile_assets_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=mobile_assets_dir), name="static")

class LoginRequest(BaseModel):
    name: str
    pin: str

@app.post("/api/login")
def login(req: LoginRequest):
    worker = worker_service.authenticate_worker(req.name, req.pin)
    if not worker:
        raise HTTPException(status_code=401, detail="Invalid name or PIN")
    return {"status": "success", "worker": worker}

class WorkEntryRequest(BaseModel):
    garment_type: Optional[str] = None
    quantity: int = 0
    bill_number: Optional[str] = None
    extra_work_description: Optional[str] = None
    extra_amount: float = 0.0

@app.post("/api/worker/{worker_id}/work-entry")
def submit_work_entry(worker_id: int, req: WorkEntryRequest):
    res = worker_service.submit_work_entry(
        worker_id=worker_id,
        garment_type=req.garment_type,
        quantity=req.quantity,
        bill_number=req.bill_number,
        extra_work_description=req.extra_work_description,
        extra_amount=req.extra_amount
    )
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return {"status": "success", "entry": res}

@app.get("/api/worker/{worker_id}/entries")
def get_worker_entries(worker_id: int):
    entries = worker_service.get_worker_entries(worker_id)
    return {"status": "success", "entries": entries}

@app.get("/api/worker/{worker_id}/ledger")
def get_worker_ledger(worker_id: int):
    ledger = worker_service.get_worker_ledger(worker_id)
    return {"status": "success", "ledger": ledger}

@app.get("/api/garment-rates")
def get_garment_rates():
    rates = worker_service.get_garment_rates()
    return {"status": "success", "rates": rates}

@app.get("/", response_class=HTMLResponse)
def index():
    # Return the mobile portal HTML
    index_path = os.path.join(mobile_assets_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return f.read()
    return "<h1>Worker Portal not found</h1>"

class WebServerThread(Thread):
    def __init__(self, host="0.0.0.0", port=8000):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.server = None

    def run(self):
        logger.info(f"Starting Worker Portal server on {self.host}:{self.port}")
        config = uvicorn.Config(app, host=self.host, port=self.port, log_level="info", access_log=False)
        self.server = uvicorn.Server(config)
        self.server.run()
        
    def stop(self):
        if self.server:
            self.server.should_exit = True
