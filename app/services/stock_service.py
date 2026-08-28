from __future__ import annotations
from app.database.engine import get_session
from app.repositories.stock_repo import StockRepository
from app.models.stock import StockItem
from app.utils.logger import get_logger

logger = get_logger(__name__)

class StockService:
    
    def get_all_stock(self) -> list[StockItem]:
        session = get_session()
        try:
            return StockRepository(session).get_all()
        finally:
            session.close()

    def get_low_stock_items(self) -> list[StockItem]:
        session = get_session()
        try:
            return StockRepository(session).get_low_stock()
        finally:
            session.close()

    def add_stock_item(self, name: str, category: str, quantity: float, unit: str, min_quantity: float) -> dict:
        session = get_session()
        try:
            repo = StockRepository(session)
            item = repo.create(
                name=name,
                category=category,
                quantity=quantity,
                unit=unit,
                min_quantity=min_quantity
            )
            session.commit()
            logger.info(f"Added stock item: {name}")
            return {"id": item.id, "name": item.name, "quantity": item.quantity}
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to add stock item: {e}")
            raise
        finally:
            session.close()

    def update_stock_item(self, item_id: int, name: str, category: str, unit: str, min_quantity: float) -> dict:
        session = get_session()
        try:
            repo = StockRepository(session)
            item = repo.update(item_id, name, category, unit, min_quantity)
            if not item:
                raise ValueError("Stock item not found")
            session.commit()
            return {"id": item.id, "name": item.name}
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def adjust_stock(self, item_id: int, amount: float, operation: str, worker_id: int = None) -> dict:
        """
        Adjust stock quantity. 
        `amount` is absolute value. `operation` is "add" or "consume".
        """
        session = get_session()
        try:
            repo = StockRepository(session)
            item = repo.get_by_id(item_id)
            if not item:
                raise ValueError("Stock item not found")
                
            if operation == "consume":
                if item.quantity < amount:
                    raise ValueError(f"Insufficient stock. Available: {item.quantity}, Requested: {amount}")
                item.quantity -= amount
                
                # Log usage if worker is provided
                if worker_id is not None:
                    from app.models.stock import StockUsage
                    usage = StockUsage(worker_id=worker_id, stock_item_id=item_id, quantity=amount)
                    session.add(usage)
            elif operation == "add":
                item.quantity += amount
            else:
                raise ValueError("Invalid operation. Must be 'add' or 'consume'")
                
            session.commit()
            logger.info(f"Adjusted stock {item.id} by {amount} ({operation}). New qty: {item.quantity}")
            return {"id": item.id, "quantity": item.quantity, "name": item.name}
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_stock_item(self, item_id: int) -> bool:
        session = get_session()
        try:
            repo = StockRepository(session)
            result = repo.delete(item_id)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

# Singleton instance for use across the app if needed, though they can be instantiated directly
stock_service = StockService()
