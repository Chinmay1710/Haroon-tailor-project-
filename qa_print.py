import sys
import app.models.customer
import app.models.measurement
import app.models.order
import app.models.payment
import app.models.expense
import app.models.settings

from app.database.engine import get_session
from app.services.print_service import PrintService
from app.services.order_service import OrderService

print("========================================")
print("TESTING PRINT MODULE")
print("========================================")

session = get_session()
try:
    order_srv = OrderService()
    orders = order_srv.get_all_orders()
    if not orders:
        print("No orders to print.")
        sys.exit(0)
        
    order = orders[0]
    print_srv = PrintService(session)
    
    # Generate receipt PDF
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "receipt.pdf")
        pdf_path = print_srv.generate_receipt_pdf(order.id, path)
        if os.path.exists(pdf_path):
            print("PASS: Receipt PDF generated ->", pdf_path)
            print("PDF Size:", os.path.getsize(pdf_path))
        else:
            print("FAIL: Receipt PDF not generated.")
            
        path_slip = os.path.join(d, "slip.pdf")
        slip_path = print_srv.generate_stitching_slip(order.id, path_slip)
        if os.path.exists(slip_path):
            print("PASS: Stitching Slip PDF generated ->", slip_path)
        else:
            print("FAIL: Stitching Slip PDF not generated.")

except Exception as e:
    print("UNEXPECTED QA ERROR:", e)
finally:
    session.close()
