import sys
from datetime import date
from sqlalchemy.exc import IntegrityError, StatementError
import os

from app.database.engine import get_session, close_db
from app.services.customer_service import CustomerService
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.repositories.measurement_repo import MeasurementRepository
from app.services.report_service import ReportService
from app.models.customer import Customer
from app.models.order import Order

def run_qa_tests():
    print("========================================")
    print("STARTING FINAL PRODUCTION QA PASS")
    print("========================================")
    
    session = get_session()
    
    try:
        # ----------------------------------------------------
        # 1. TEST VALIDATION
        # ----------------------------------------------------
        print("\n--- TEST VALIDATION ---")
        cust_srv = CustomerService()
        
        # Empty customer name rejected
        try:
            cust_srv.create_customer("", "123", "addr", "VIP")
            print("FAIL: Empty customer name allowed.")
        except Exception as e:
            print("PASS: Empty customer name rejected.", e)

        print("\n--- TEST REAL USER WORKFLOW ---")
        # Add Customer
        customer = cust_srv.create_customer("QA Workflow User", "5556667777", "QA Address", "VIP")
        print("Customer Created:", customer.id)
        
        # Create Measurement
        meas_repo = MeasurementRepository(session)
        profile = meas_repo.create_profile(customer.id, "Shirt", "QA Fit", "inches")
        meas_repo.add_value(profile.id, "length", "30", 1)
        session.commit()
        print("Measurement Profile Created:", profile.id)
        
        # Create New Order & Advance
        order_srv = OrderService()
        order = order_srv.create_order(
            customer_id=customer.id,
            clothing_type="Shirt",
            measurement_profile_id=profile.id,
            quantity=1,
            price=2000,
            order_date=date.today(),
            delivery_date=date.today(),
            special_instructions="QA Notes",
            advance_amount=500,
            payment_method="CASH"
        )
        print("Order Created:", order.order_number)
        
        # Status Changes
        order = order_srv.update_status(order.id, "STITCHING")
        order = order_srv.update_status(order.id, "READY")
        
        # Payment greater than outstanding rejected
        pay_srv = PaymentService()
        rem = order.remaining_amount
        try:
            pay_srv.add_payment(order.id, rem + 100, date.today(), "CASH")
            print("FAIL: Overpayment allowed.")
        except ValueError as e:
            print("PASS: Overpayment rejected:", e)
            
        # Add Remaining Payment
        pay = pay_srv.add_payment(order.id, rem, date.today(), "CASH")
        order = order_srv.get_order(order.id)
        if order.remaining_amount == 0:
            print("PASS: Balance is 0.")
        else:
            print("FAIL: Balance is not 0:", order.remaining_amount)
            
        # Mark DELIVERED
        order = order_srv.update_status(order.id, "DELIVERED")
        print("Order Delivered.")
        
        # ----------------------------------------------------
        # 2. TEST REPORTS / DASHBOARD
        # ----------------------------------------------------
        rep_srv = ReportService()
        data = rep_srv.get_today_report()
        print(f"Reports Today - Sales: {data['total_sales']}, Orders: {data['completed_orders']}")
        
        # ----------------------------------------------------
        # 3. TEST BACKUP / RESTORE
        # ----------------------------------------------------
        from app.services.backup_service import BackupService
        backup_srv = BackupService()
        import tempfile
        import glob
        
        with tempfile.TemporaryDirectory() as d:
            backup_srv.create_backup(d)
            files = glob.glob(os.path.join(d, "*.db"))
            if files:
                backup_file = files[0]
                print("PASS: Backup created successfully at", backup_file)
            else:
                print("FAIL: Backup file not found.")
                backup_file = None
                
            if backup_file:
                # Modify data
                cust_srv.create_customer("SHOULD BE RESTORED AWAY", "0", "", "")
                
                # Close DB before restore!
                close_db()
                
                # Restore using the specific file
                backup_srv.restore_backup(backup_file)
                print("PASS: Restore executed.")
            
        # Check if the new user is gone
        session2 = get_session()
        cust_srv = CustomerService()
        users = cust_srv.search_customers("SHOULD BE RESTORED AWAY")
        if len(users) == 0:
            print("PASS: Database returned to backup state.")
        else:
            print("FAIL: Database restore failed, modifications persisted.")
            print(users)

        # ----------------------------------------------------
        # 4. REMOVE TEST DATA
        # ----------------------------------------------------
        session2.query(Order).filter(Order.customer_id == customer.id).delete()
        session2.query(Customer).filter(Customer.id == customer.id).delete()
        session2.commit()
        print("Test data cleaned up.")

    except Exception as e:
        print("UNEXPECTED QA ERROR:", e)
    finally:
        close_db()

if __name__ == "__main__":
    run_qa_tests()
