# @Author: Sheep Wang
# @File: payment_DAO.py
# @Created: 2026-09-06 22:52
# @Description: payment_DAO.py


from datetime import datetime
import uuid
from utils.DB_utils import get_db_connection




class PaymentDAO:

    @staticmethod
    def process_payment_transaction(username: str, order_id: str, payment_method: str, payment_amount: float) -> bool:
        """
        Executes payment within a database transaction:
        1. Resolves user_id from username.
        2. Locks the order (FOR UPDATE) and checks its existence, ownership, and PENDING_PAY status.
        3. Validates if payment_amount matches order total_amount.
        4. Inserts a record into `payments` table.
        5. Updates `orders` status to `PAID`.
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 1. Get user_id from users table
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                user_record = cursor.fetchone()
                if not user_record:
                    conn.rollback()
                    return False
                user_id = user_record["id"]

                # 2. Fetch and lock the order
                cursor.execute(
                    "SELECT total_amount, status FROM orders WHERE order_id = %s AND user_id = %s FOR UPDATE",
                    (order_id, user_id)
                )
                order = cursor.fetchone()

                if not order:
                    conn.rollback()
                    return False  # Order not found or not owned by user

                if order["status"] != "PENDING_PAY":
                    conn.rollback()
                    return False  # Order already paid or cancelled

                # 3. Validate payment amount
                expected_amount = float(order["total_amount"])
                if abs(expected_amount - payment_amount) > 1e-6:
                    conn.rollback()
                    return False  # Amount mismatch

                # 4. Generate mock third-party transaction id
                transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"

                # 5. Insert into payments table
                cursor.execute(
                    """
                    INSERT INTO payments (order_id, payment_amount, payment_method, status, transaction_id, paid_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    """,
                    (order_id, payment_amount, payment_method, "SUCCESS", transaction_id)
                )

                # 6. Update order status to PAID
                cursor.execute(
                    "UPDATE orders SET status = %s WHERE order_id = %s",
                    ("PAID", order_id)
                )

                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_payment_by_order_id(order_id: str) -> list:
        """Retrieves payment history for a specific order."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM payments WHERE order_id = %s",
                    (order_id,)
                )
                return cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            conn.close()