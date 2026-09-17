# @Author: Sheep Wang
# @File: orders_api.py
# @Created: 2026-09-17 22:39
# @Description: orders_api.py



from fastapi import APIRouter, Depends
from model.orders_model import (
    OrderCreateRequest,
    BatchOrderCreateRequest,
    OrderCancelRequest,
    OrderStatusUpdateRequest,
    BatchOrderQueryRequest,
    OrderDetailResponse
)
from service.orders_service import OrdersService
from utils.auth import get_current_user
from utils.response import BaseResponse
from utils.logger import logger




router = APIRouter(prefix="/orders", tags=["Order Management"])





@router.post("", response_model=BaseResponse)
def create_order_api(data: OrderCreateRequest, current_user: str = Depends(get_current_user)):
    """Creates a single order with inventory locking and transaction control."""
    logger.info(f"API: Single order creation requested by '{current_user}'")
    return OrdersService.create_order(username=current_user, data=data)

@router.post("/batch", response_model=BaseResponse)
def batch_create_orders_api(data: BatchOrderCreateRequest, current_user: str = Depends(get_current_user)):
    """Creates multiple orders in a single atomic transaction (Batch Create)."""
    logger.info(f"API: Batch order creation requested by '{current_user}'")
    return OrdersService.batch_create_orders(username=current_user, data=data)

@router.post("/cancel", response_model=BaseResponse)
def cancel_order_api(data: OrderCancelRequest, current_user: str = Depends(get_current_user)):
    """Cancels a single unpaid order and rolls back stock (Non-batch)."""
    logger.info(f"API: Cancel order ID '{data.order_id}' requested by '{current_user}'")
    return OrdersService.cancel_order(username=current_user, order_id=data.order_id)

@router.post("/status", response_model=BaseResponse)
def update_order_status_api(data: OrderStatusUpdateRequest, current_user: str = Depends(get_current_user)):
    """Updates a single order's status directly (Non-batch)."""
    logger.info(f"API: Update status for order ID '{data.order_id}' to '{data.status}'")
    return OrdersService.update_status(order_id=data.order_id, new_status=data.status)

@router.get("/{order_id}", response_model=BaseResponse[OrderDetailResponse])
def get_order_detail_api(order_id: str, current_user: str = Depends(get_current_user)):
    """Retrieves full aggregated details for a single order (Master-Detail)."""
    logger.info(f"API: Get detail for order ID '{order_id}' by '{current_user}'")
    return OrdersService.get_order_detail(username=current_user, order_id=order_id)

@router.post("/batch-query", response_model=BaseResponse)
def batch_get_orders_api(data: BatchOrderQueryRequest, current_user: str = Depends(get_current_user)):
    """Retrieves aggregated details for multiple orders at once (Batch Query)."""
    logger.info(f"API: Batch query orders requested by '{current_user}'")
    return OrdersService.batch_get_orders(username=current_user, data=data)