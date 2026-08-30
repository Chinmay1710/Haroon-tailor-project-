import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.engine import get_session
from app.models.worker import Worker, WorkerTask, GarmentRate, WorkEntry, WorkerAdvance, WorkerType, WorkerRole
from app.models.stock import StockUsage, StockItem
from app.models.order import OrderItem, Order

logger = logging.getLogger(__name__)

class WorkerService:
    def __init__(self):
        pass

    def get_all_workers(self) -> List[Dict[str, Any]]:
        with get_session() as session:
            workers = session.query(Worker).all()
            
            result = []
            for w in workers:
                total_earned = session.query(func.sum(WorkEntry.total_amount)).filter(
                    WorkEntry.worker_id == w.id, 
                    WorkEntry.status == "APPROVED",
                    WorkEntry.is_settled == False
                ).scalar() or 0.0
                
                total_advance = session.query(func.sum(WorkerAdvance.amount)).filter(
                    WorkerAdvance.worker_id == w.id,
                    WorkerAdvance.is_settled == False
                ).scalar() or 0.0

                result.append({
                    "id": w.id,
                    "name": w.name,
                    "phone": w.phone,
                    "pin": w.pin,
                    "worker_type": w.worker_type,
                    "worker_role": getattr(w, "worker_role", WorkerRole.STITCHING.value),
                    "daily_rate": w.daily_rate,
                    "is_active": w.is_active,
                    "created_at": w.created_at.isoformat() if w.created_at else None,
                    "ledger": {
                        "total_earned": total_earned,
                        "total_advance": total_advance,
                        "remaining_balance": total_earned - total_advance
                    }
                })
            return result

    def add_worker(self, name: str, phone: str, pin: str, worker_type: str = WorkerType.PIECE_RATE.value, worker_role: str = WorkerRole.STITCHING.value, daily_rate: float = 0.0) -> Dict[str, Any]:
        with get_session() as session:
            worker = Worker(name=name, phone=phone, pin=pin, worker_type=worker_type, worker_role=worker_role, daily_rate=daily_rate)
            session.add(worker)
            session.commit()
            session.refresh(worker)
            return {"id": worker.id, "name": worker.name}

    def authenticate_worker(self, name: str, pin: str) -> Optional[Dict[str, Any]]:
        with get_session() as session:
            clean_name = name.strip().lower()
            clean_pin = pin.strip()
            worker = session.query(Worker).filter(
                func.lower(func.trim(Worker.name)) == clean_name, 
                func.trim(Worker.pin) == clean_pin, 
                Worker.is_active == True
            ).first()
            if worker:
                return {"id": worker.id, "name": worker.name, "pin": worker.pin, "worker_type": worker.worker_type, "worker_role": getattr(worker, "worker_role", WorkerRole.STITCHING.value)}
            return None

    # --- Garment Rates ---

    def get_garment_rates(self) -> List[Dict[str, Any]]:
        with get_session() as session:
            rates = session.query(GarmentRate).all()
            return [{"id": r.id, "garment_type": r.garment_type, "rate": r.rate} for r in rates]

    def set_garment_rate(self, garment_type: str, rate: float) -> Dict[str, Any]:
        with get_session() as session:
            g_rate = session.query(GarmentRate).filter(GarmentRate.garment_type == garment_type).first()
            if g_rate:
                g_rate.rate = rate
            else:
                g_rate = GarmentRate(garment_type=garment_type, rate=rate)
                session.add(g_rate)
            session.commit()
            session.refresh(g_rate)
            return {"id": g_rate.id, "garment_type": g_rate.garment_type, "rate": g_rate.rate}

    # --- Work Entries ---

    def submit_work_entry(self, worker_id: int, garment_type: Optional[str], quantity: int, bill_number: Optional[str], extra_work_description: Optional[str], extra_amount: float, auto_approve: bool = False, is_present: bool = False) -> Dict[str, Any]:
        with get_session() as session:
            worker = session.query(Worker).get(worker_id)
            if not worker:
                return {"error": "Worker not found"}

            total_amount = extra_amount
            if worker.worker_type == WorkerType.PIECE_RATE.value and garment_type:
                g_rate = session.query(GarmentRate).filter(GarmentRate.garment_type == garment_type).first()
                if g_rate:
                    total_amount += (g_rate.rate * quantity)
            elif worker.worker_type == WorkerType.DAILY_SALARY.value:
                # For daily salary workers, only add their daily rate if marked present
                if is_present:
                    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                    already_present = session.query(WorkEntry).filter(
                        WorkEntry.worker_id == worker_id,
                        WorkEntry.entry_date >= today_start,
                        WorkEntry.total_amount > WorkEntry.extra_amount
                    ).first()
                    if not already_present:
                        total_amount += worker.daily_rate

            entry = WorkEntry(
                worker_id=worker_id,
                garment_type=garment_type,
                quantity=quantity,
                bill_number=bill_number,
                extra_work_description=extra_work_description,
                extra_amount=extra_amount,
                total_amount=total_amount,
                status="APPROVED" if auto_approve else "PENDING"
            )
            session.add(entry)
            session.commit()
            session.refresh(entry)
            return {"id": entry.id, "status": entry.status}
            
    def edit_pending_entry(self, entry_id: int, new_quantity: int, new_extra_amount: float, new_total_amount: float) -> Dict[str, Any]:
        with get_session() as session:
            entry = session.query(WorkEntry).filter(WorkEntry.id == entry_id).first()
            if not entry:
                return {"error": "Entry not found"}
            if entry.status != "PENDING":
                return {"error": "Only pending entries can be edited"}
                
            entry.quantity = new_quantity
            entry.extra_amount = new_extra_amount
            entry.total_amount = new_total_amount
            
            session.commit()
            session.refresh(entry)
            return {"id": entry.id, "status": "updated"}

    def get_worker_entries(self, worker_id: int) -> List[Dict[str, Any]]:
        with get_session() as session:
            entries = session.query(WorkEntry).filter(WorkEntry.worker_id == worker_id).order_by(WorkEntry.entry_date.desc()).all()
            return [{
                "id": e.id,
                "entry_date": e.entry_date.isoformat(),
                "garment_type": e.garment_type,
                "quantity": e.quantity,
                "bill_number": e.bill_number,
                "extra_work_description": e.extra_work_description,
                "extra_amount": e.extra_amount,
                "total_amount": e.total_amount,
                "status": e.status
            } for e in entries]

    def get_all_pending_entries(self) -> List[Dict[str, Any]]:
         with get_session() as session:
            entries = session.query(WorkEntry).filter(WorkEntry.status == "PENDING").order_by(WorkEntry.entry_date.desc()).all()
            return [{
                "id": e.id,
                "worker_id": e.worker_id,
                "worker_name": e.worker.name if e.worker else "Unknown",
                "entry_date": e.entry_date.isoformat(),
                "garment_type": e.garment_type,
                "quantity": e.quantity,
                "bill_number": e.bill_number,
                "extra_work_description": e.extra_work_description,
                "extra_amount": e.extra_amount,
                "total_amount": e.total_amount,
                "status": e.status
            } for e in entries]

    def approve_entry(self, entry_id: int, status: str) -> bool:
        with get_session() as session:
            entry = session.query(WorkEntry).get(entry_id)
            if entry and status in ["APPROVED", "REJECTED"]:
                entry.status = status
                session.commit()
                return True
            return False

    # --- Advances ---

    def record_advance(self, worker_id: int, amount: float, notes: str = "") -> Dict[str, Any]:
        with get_session() as session:
            advance = WorkerAdvance(worker_id=worker_id, amount=amount, notes=notes)
            session.add(advance)
            session.commit()
            session.refresh(advance)
            return {"id": advance.id, "amount": advance.amount}

    # --- Ledger ---

    def get_worker_ledger(self, worker_id: int) -> Dict[str, Any]:
        with get_session() as session:
            worker = session.query(Worker).get(worker_id)
            if not worker:
                return {}

            total_earned = session.query(func.sum(WorkEntry.total_amount)).filter(
                WorkEntry.worker_id == worker_id, 
                WorkEntry.status == "APPROVED",
                WorkEntry.is_settled == False
            ).scalar() or 0.0
            
            total_advance = session.query(func.sum(WorkerAdvance.amount)).filter(
                WorkerAdvance.worker_id == worker_id,
                WorkerAdvance.is_settled == False
            ).scalar() or 0.0

            return {
                "worker_id": worker_id,
                "worker_name": worker.name,
                "total_earned": total_earned,
                "total_advance": total_advance,
                "remaining_balance": total_earned - total_advance
            }
            
    def settle_worker_account(self, worker_id: int) -> bool:
        """Mark all existing work entries and advances for this worker as settled."""
        with get_session() as session:
            worker = session.query(Worker).get(worker_id)
            if not worker:
                return False
                
            session.query(WorkEntry).filter(WorkEntry.worker_id == worker_id, WorkEntry.is_settled == False).update({"is_settled": True})
            session.query(WorkerAdvance).filter(WorkerAdvance.worker_id == worker_id, WorkerAdvance.is_settled == False).update({"is_settled": True})
            session.commit()
            return True

    def delete_worker(self, worker_id: int) -> bool:
        """Delete a worker and all their related entries (work entries, advances, tasks)."""
        with get_session() as session:
            worker = session.query(Worker).get(worker_id)
            if not worker:
                return False
            # Delete related records first
            session.query(WorkEntry).filter(WorkEntry.worker_id == worker_id).delete()
            session.query(WorkerAdvance).filter(WorkerAdvance.worker_id == worker_id).delete()
            session.query(WorkerTask).filter(WorkerTask.worker_id == worker_id).delete()
            session.delete(worker)
            session.commit()
            return True

    def get_worker_history(self, worker_id: int) -> Dict[str, Any]:
        """Get combined work entries and advances for a worker, sorted by date."""
        with get_session() as session:
            worker = session.query(Worker).get(worker_id)
            if not worker:
                return {"worker_name": "Unknown", "history": []}

            # Get work entries
            entries = session.query(WorkEntry).filter(
                WorkEntry.worker_id == worker_id
            ).order_by(WorkEntry.entry_date.desc()).all()

            # Get advances
            advances = session.query(WorkerAdvance).filter(
                WorkerAdvance.worker_id == worker_id
            ).order_by(WorkerAdvance.date.desc()).all()

            history = []
            for e in entries:
                desc = ""
                if e.garment_type:
                    desc = f"{e.quantity}x {e.garment_type}"
                if e.extra_work_description:
                    desc += f" + {e.extra_work_description}" if desc else e.extra_work_description
                if not desc:
                    desc = "Daily Salary"

                history.append({
                    "type": "WORK",
                    "date": e.entry_date.isoformat() if e.entry_date else "",
                    "description": desc,
                    "amount": e.total_amount,
                    "status": e.status,
                    "extra_amount": e.extra_amount or 0,
                    "is_settled": e.is_settled
                })

            for a in advances:
                history.append({
                    "type": "ADVANCE",
                    "date": a.date.isoformat() if a.date else "",
                    "description": a.notes or "Advance Payment",
                    "amount": a.amount,
                    "status": "PAID",
                    "extra_amount": 0,
                    "is_settled": a.is_settled
                })

            # Sort combined history by date descending
            history.sort(key=lambda x: x["date"], reverse=True)

            return {
                "worker_name": worker.name,
                "history": history
            }

    def get_stock_usage_history(self) -> List[Dict[str, Any]]:
        with get_session() as session:
            usages = session.query(StockUsage, Worker.name, StockItem.name, StockItem.unit).join(
                Worker, StockUsage.worker_id == Worker.id
            ).join(
                StockItem, StockUsage.stock_item_id == StockItem.id
            ).order_by(StockUsage.date.desc()).all()
            
            return [
                {
                    "id": usage[0].id,
                    "worker_name": usage[1],
                    "item_name": usage[2],
                    "quantity": usage[0].quantity,
                    "unit": usage[3],
                    "date": usage[0].date.isoformat()
                }
                for usage in usages
            ]

worker_service = WorkerService()
