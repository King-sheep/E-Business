# @Author: Sheep Wang
# @File: orders_service.py
# @Created: 2026-09-17 22:38
# @Description: orders_service.py


from DAO.orders_DAO import OrdersDAO
from model.orders_model import OrderCreateRequest, BatchOrderCreateRequest, BatchOrderQueryRequest
from utils.response import success, fail
from utils.logger import logger





class OrdersService:

    @staticmethod
    def create_order(username: str, data: OrderCreateRequest):
        """Handles single order creation."""
        logger.info(f"Service: User '{username}' creating a single order.")

        try:
            order_id, total_amount = OrdersDAO.create_order_transaction(username, data.items)
            if order_id:
                return success(data={"order_id": order_id, "total_amount": total_amount, "status": "PENDING_PAY"}, msg="Order created successfully")
            return fail(msg="Failed to create order: out of stock or product not found", code=400)
        except Exception as e:
            logger.error(f"Create order exception: {str(e)}")
            return fail(msg=f"Failed to create order: {str(e)}", code=400)

    @staticmethod
    def batch_create_orders(username: str, data: BatchOrderCreateRequest):
        """Handles batch order creation."""
        logger.info(f"Service: User '{username}' batch creating orders.")

        try: 
            order_ids_amts = OrdersDAO.batch_create_orders_transaction(username, data.orders)
            if order_ids_amts:
                return success(data={"order_ids_amts": order_ids_amts}, msg="Batch orders created successfully")
            return fail(msg="Batch creation failed: stock insufficient", code=400)
        except Exception as e:
            logger.error(f"Create order exception: {str(e)}")
            return fail(msg=f"Failed to create order: {str(e)}", code=400)

    @staticmethod
    def cancel_order(username: str, order_id: str):
        """Handles single order cancellation (Non-batch)."""
        logger.info(f"Service: User '{username}' canceling order '{order_id}'.")
        success_flag = OrdersDAO.cancel_order_transaction(order_id, username)
        if success_flag:
            return success(msg="Order cancelled successfully, stock restored")
        return fail(msg="Failed to cancel order: not found or invalid status", code=400)

    @staticmethod
    def update_status(order_id: str, new_status: str):
        """Handles single status update (Non-batch)."""
        logger.info(f"Service: Updating order '{order_id}' status to '{new_status}'.")
        success_flag = OrdersDAO.update_order_status(order_id, new_status)
        if success_flag:
            return success(msg="Order status updated successfully")
        return fail(msg="Order not found or update failed", code=404)

    @staticmethod
    def get_order_detail(username: str, order_id: str):
        """Handles single aggregated order retrieval."""
        logger.info(f"Service: Fetching detail for order '{order_id}'.")
        order_detail = OrdersDAO.get_order_detail(order_id, username)
        if order_detail:
            return success(data=order_detail, msg="Order detail retrieved successfully")
        return fail(msg="Order not found or access denied", code=404)

    @staticmethod
    def batch_get_orders(username: str, data: BatchOrderQueryRequest):
        """Handles batch aggregated order retrieval."""
        logger.info(f"Service: User '{username}' batch querying orders.")
        orders_list = OrdersDAO.batch_get_orders_detail(data.order_ids, username)
        return success(data=orders_list, msg="Batch orders retrieved successfully")