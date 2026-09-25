# @Author: Sheep Wang
# @File: orders_DAO.py
# @Created: 2026-09-17 22:37
# @Description: orders_DAO.py



from datetime import datetime
import uuid
from utils.DB_utils import get_db_connection





class OrdersDAO:

    @staticmethod
    def create_order_transaction(username: str, items: list) -> str | None:
        """
        Executes single order creation within a transaction:
        1. Resolves user_id from username.
        2. Locks inventory (FOR UPDATE) and calculates total amount.
        3. Inserts master order and batch inserts order items.
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                user_record = cursor.fetchone()
                if not user_record:
                    conn.rollback()
                    return None
                user_id = user_record["id"]

                order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
                total_amount = 0.0
                order_items_to_insert = []

                for item in items:
                    cursor.execute(
                        "SELECT name, price, stock FROM products WHERE id = %s FOR UPDATE",
                        (item.product_id,)
                    )
                    product = cursor.fetchone()
                    if not product or product["stock"] < item.quantity:
                        conn.rollback()
                        return None

                    p_name = product["name"]
                    p_price = float(product["price"])
                    total_amount += p_price * item.quantity

                    order_items_to_insert.append(
                        (order_id, item.product_id, p_name, p_price, item.quantity)
                    )

                    cursor.execute(
                        "UPDATE products SET stock = stock - %s WHERE id = %s",
                        (item.quantity, item.product_id)
                    )

                cursor.execute(
                    "INSERT INTO orders (order_id, user_id, total_amount, status) VALUES (%s, %s, %s, %s)",
                    (order_id, user_id, total_amount, "PENDING_PAY")
                )

                cursor.executemany(
                    """
                    INSERT INTO order_items (order_id, product_id, product_name, price, quantity)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    order_items_to_insert
                )

                conn.commit()
                return order_id, total_amount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def batch_create_orders_transaction(username: str, batch_data: list) -> list | None:
        """
        Batch creates multiple orders in a single atomic transaction.
        Rolls back all changes if any item lacks sufficient stock.
        """
        conn = get_db_connection()
        created_order_ids_amts = []
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                user_record = cursor.fetchone()
                if not user_record:
                    conn.rollback()
                    return None
                user_id = user_record["id"]

                for order_req in batch_data:
                    order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
                    total_amount = 0.0
                    order_items_to_insert = []

                    for item in order_req.items:
                        cursor.execute(
                            "SELECT name, price, stock FROM products WHERE id = %s FOR UPDATE",
                            (item.product_id,)
                        )
                        product = cursor.fetchone()
                        if not product or product["stock"] < item.quantity:
                            conn.rollback()
                            return None

                        p_name = product["name"]
                        p_price = float(product["price"])
                        total_amount += p_price * item.quantity

                        order_items_to_insert.append(
                            (order_id, item.product_id, p_name, p_price, item.quantity)
                        )

                        cursor.execute(
                            "UPDATE products SET stock = stock - %s WHERE id = %s",
                            (item.quantity, item.product_id)
                        )

                    cursor.execute(
                        "INSERT INTO orders (order_id, user_id, total_amount, status) VALUES (%s, %s, %s, %s)",
                        (order_id, user_id, total_amount, "PENDING_PAY")
                    )

                    cursor.executemany(
                        """
                        INSERT INTO order_items (order_id, product_id, product_name, price, quantity)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        order_items_to_insert
                    )
                    created_order_ids_amts.append({"order_id":order_id, "total_amount": total_amount})

                conn.commit()
                return created_order_ids_amts
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def cancel_order_transaction(order_id: str, username: str) -> bool:
        """
        Cancels a single unpaid order and restores product stock. (Non-batch operation)
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                user_record = cursor.fetchone()
                if not user_record:
                    conn.rollback()
                    return False
                user_id = user_record["id"]

                cursor.execute(
                    "SELECT status FROM orders WHERE order_id = %s AND user_id = %s FOR UPDATE",
                    (order_id, user_id)
                )
                order = cursor.fetchone()
                if not order or order["status"] != "PENDING_PAY":
                    conn.rollback()
                    return False

                cursor.execute(
                    "SELECT product_id, quantity FROM order_items WHERE order_id = %s",
                    (order_id,)
                )
                items = cursor.fetchall()

                for item in items:
                    cursor.execute(
                        "UPDATE products SET stock = stock + %s WHERE id = %s",
                        (item["quantity"], item["product_id"])
                    )

                cursor.execute(
                    "UPDATE orders SET status = %s WHERE order_id = %s",
                    ("CANCELLED", order_id)
                )

                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def update_order_status(order_id: str, new_status: str) -> bool:
        """
        Directly updates a single order status. (Non-batch operation)
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE orders SET status = %s WHERE order_id = %s",
                    (new_status, order_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_order_detail(order_id: str, username: str) -> dict | None:
        """
        Retrieves complete aggregated details for a single order.
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                user_record = cursor.fetchone()
                if not user_record:
                    return None
                user_id = user_record["id"]

                cursor.execute(
                    "SELECT * FROM orders WHERE order_id = %s AND user_id = %s",
                    (order_id, user_id)
                )
                order = cursor.fetchone()
                if not order:
                    return None

                cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
                items = cursor.fetchall()

                cursor.execute("SELECT * FROM payments WHERE order_id = %s", (order_id,))
                payments = cursor.fetchall()

                return {
                    "order": order,
                    "items": items,
                    "payments": payments
                }
        except Exception as e:
            raise e
        finally:
            conn.close()
            

    @staticmethod
    def batch_get_orders_detail(order_ids: list, username: str) -> list:
        """
        Retrieves aggregated details for multiple orders in batch.
        """
        conn = get_db_connection()
        results = []
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                user_record = cursor.fetchone()
                if not user_record:
                    return []
                user_id = user_record["id"]

                for order_id in order_ids:
                    cursor.execute(
                        "SELECT * FROM orders WHERE order_id = %s AND user_id = %s",
                        (order_id, user_id)
                    )
                    order = cursor.fetchone()
                    if not order:
                        continue

                    cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
                    items = cursor.fetchall()

                    cursor.execute("SELECT * FROM payments WHERE order_id = %s", (order_id,))
                    payments = cursor.fetchall()

                    results.append({
                        "order": order,
                        "items": items,
                        "payments": payments
                    })
                return results
        except Exception as e:
            raise e
        finally:
            conn.close()