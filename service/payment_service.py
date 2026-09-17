# @Author: Sheep Wang
# @File: payment_service.py
# @Created: 2026-09-06 22:52
# @Description: payment_service.py


from DAO.payment_DAO import PaymentDAO
from model.payment_model import PaymentCreateRequest
from utils.response import success, fail
from utils.logger import logger




class PaymentService:

    @staticmethod
    def pay_order(username: str, data: PaymentCreateRequest):
        """Processes payment for an existing unpaid order."""
        logger.info(f"Service: User '{username}' attempting to pay for order '{data.order_id}' with amount {data.payment_amount}.")
        
        success_flag = PaymentDAO.process_payment_transaction(
            username=username,
            order_id=data.order_id,
            payment_method=data.payment_method,
            payment_amount=data.payment_amount
        )

        if success_flag:
            logger.info(f"Service: Payment succeeded for order '{data.order_id}' by user '{username}'.")
            return success(msg="Payment processed successfully")

        logger.warning(f"Service: Payment failed for order '{data.order_id}' by user '{username}'. Invalid status, wrong amount, or order not found.")
        return fail(msg="Payment failed: invalid order, amount mismatch, or order already paid/cancelled", code=400)


    @staticmethod
    def get_payments(order_id: str):
        """Retrieves payment details for an order."""
        logger.info(f"Service: Fetching payment records for order '{order_id}'.")
        payments = PaymentDAO.get_payment_by_order_id(order_id)
        return success(data=payments, msg="Payment records retrieved successfully")