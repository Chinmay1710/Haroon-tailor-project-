from sqlalchemy.orm import Session
from sqlalchemy import asc
from app.models.stock import StockItem

class StockRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[StockItem]:
        return self.session.query(StockItem).order_by(asc(StockItem.name)).all()

    def get_by_id(self, item_id: int) -> StockItem | None:
        return self.session.query(StockItem).filter(StockItem.id == item_id).first()

    def get_low_stock(self) -> list[StockItem]:
        return self.session.query(StockItem).filter(StockItem.quantity <= StockItem.min_quantity).order_by(asc(StockItem.name)).all()

    def create(self, name: str, category: str, quantity: float, unit: str, min_quantity: float) -> StockItem:
        item = StockItem(
            name=name,
            category=category,
            quantity=quantity,
            unit=unit,
            min_quantity=min_quantity
        )
        self.session.add(item)
        return item

    def update(self, item_id: int, name: str, category: str, unit: str, min_quantity: float) -> StockItem | None:
        item = self.get_by_id(item_id)
        if item:
            item.name = name
            item.category = category
            item.unit = unit
            item.min_quantity = min_quantity
        return item

    def update_quantity(self, item_id: int, new_quantity: float) -> StockItem | None:
        item = self.get_by_id(item_id)
        if item:
            item.quantity = new_quantity
        return item

    def delete(self, item_id: int) -> bool:
        item = self.get_by_id(item_id)
        if item:
            self.session.delete(item)
            return True
        return False
