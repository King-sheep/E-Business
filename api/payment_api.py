# @Author: Sheep Wang
# @File: payment_api.py
# @Created: 2026-09-06 22:53
# @Description: payment_api.py


from fastapi import APIRouter, Depends
from model.payment_model import PaymentCreateRequest
from service.payment_service import PaymentService
from utils.auth import get_current_user
from utils.response import BaseResponse
from utils.logger import logger




router = APIRouter(prefix="/payments", tags=["Payment Management"])





@router.post("", response_model=BaseResponse)
def pay_order_api(data: PaymentCreateRequest, current_user: str = Depends(get_current_user)):
    """
    **Process Order Payment**:
    - Validates order ownership, PENDING_PAY status, and payment amount.
    - Records successful payment transaction and updates order status to `PAID`.
    - **Requires JWT Bearer Token**.
    """
    logger.info(f"API Request: Payment requested for order ID '{data.order_id}' by user: {current_user}")
    return PaymentService.pay_order(username=current_user, data=data)


@router.get("/{order_id}", response_model=BaseResponse)
def get_payment_records_api(order_id: str, current_user: str = Depends(get_current_user)):
    """
    **Get Payment Records**:
    - Retrieves payment history associated with the given order ID.
    - **Requires JWT Bearer Token**.
    """
    logger.info(f"API Request: Get payment records for order ID '{order_id}' by user: {current_user}")
    return PaymentService.get_payments(order_id=order_id)