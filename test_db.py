from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
engine = create_engine("sqlite:////Users/chinmay/Library/Application Support/TailorShopManager/data/tailor_shop.db")
Session = sessionmaker(bind=engine)
session = Session()
result = session.execute(text("SELECT status FROM orders WHERE id=21")).fetchone()
print("ORDER 21 STATUS:", result[0])
