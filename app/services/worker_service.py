import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.engine import get_session
from app.models.worker import Worker, WorkerTask
from app.models.order import OrderItem, Order

logger = logging.getLogger(__name__)

class WorkerService:
    def __init__(self):
        pass

    def get_all_workers(self) -> List[Dict[str, Any]]:
        with get_session() as session:
            workers = session.query(Worker).all()
            return [
                {
                    "id": w.id,
                    "name": w.name,
                    "phone": w.phone,
                    "pin": w.pin,
                    "is_active": w.is_active,
                    "created_at": w.created_at.isoformat() if w.created_at else None
                }
                for w in workers
            ]

    def add_worker(self, name: str, phone: str, pin: str) -> Dict[str, Any]:
        with get_session() as session:
            worker = Worker(name=name, phone=phone, pin=pin)
            session.add(worker)
            session.commit()
            session.refresh(worker)
            return {"id": worker.id, "name": worker.name}

    def assign_task(self, worker_id: int, order_item_id: int, payout_amount: float) -> Dict[str, Any]:
        with get_session() as session:
            task = WorkerTask(worker_id=worker_id, order_item_id=order_item_id, payout_amount=payout_amount)
            session.add(task)
            session.commit()
            session.refresh(task)
            return {"id": task.id, "status": task.status}

    def get_worker_tasks(self, worker_id: int) -> List[Dict[str, Any]]:
        with get_session() as session:
            tasks = session.query(WorkerTask).filter(WorkerTask.worker_id == worker_id).all()
            result = []
            for t in tasks:
                order_item = t.order_item
                order = order_item.order if order_item else None
                result.append({
                    "id": t.id,
                    "worker_id": t.worker_id,
                    "payout_amount": t.payout_amount,
                    "status": t.status,
                    "assigned_at": t.assigned_at.isoformat() if t.assigned_at else None,
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                    "clothing_type": order_item.clothing_type if order_item else "Unknown",
                    "order_number": order.order_number if order else "Unknown",
                    "customer_name": order.customer.name if order and order.customer else "Unknown"
                })
            return result

    def complete_task(self, task_id: int) -> bool:
        with get_session() as session:
            task = session.query(WorkerTask).get(task_id)
            if task and task.status == "ASSIGNED":
                task.status = "COMPLETED"
                task.completed_at = datetime.now(timezone.utc)
                session.commit()
                return True
            return False

    def authenticate_worker(self, name: str, pin: str) -> Optional[Dict[str, Any]]:
        with get_session() as session:
            worker = session.query(Worker).filter(func.lower(Worker.name) == name.lower(), Worker.pin == pin, Worker.is_active == True).first()
            if worker:
                return {"id": worker.id, "name": worker.name}
            return None

worker_service = WorkerService()
