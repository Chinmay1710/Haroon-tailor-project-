import os
import uvicorn
import logging
from threading import Thread
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.services.worker_service import worker_service
from app.config import ASSETS_DIR

logger = logging.getLogger(__name__)

app = FastAPI(title="Haroon Tailor Worker Portal")

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

@app.get("/api/tasks/{worker_id}")
def get_tasks(worker_id: int):
    tasks = worker_service.get_worker_tasks(worker_id)
    return {"status": "success", "tasks": tasks}

@app.post("/api/tasks/{task_id}/complete")
def complete_task(task_id: int):
    if worker_service.complete_task(task_id):
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="Failed to complete task")

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
