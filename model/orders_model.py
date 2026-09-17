# @Author: Sheep Wang
# @File: orders_model.py
# @Created: 2026-09-06 22:34
# @Description: orders_model.py



from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime




class OrderItemCreate(BaseModel):
    product_id: int = Field(..., description="Target product ID")
    quantity: int = Field(..., gt=0, description="Quantity to purchase")


class OrderCreateRequest(BaseModel):
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Product item list")


class BatchOrderCreateRequest(BaseModel):
    orders: List[OrderCreateRequest] = Field(..., min_length=1, description="List of orders to create")


class OrderCancelRequest(BaseModel):
    order_id: str = Field(..., description="Business order ID to be cancelled")

    @field_validator("order_id", mode="before")
    @classmethod
    def clean_order_id(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("order_id cannot be empty")
        return v


class OrderStatusUpdateRequest(BaseModel):
    order_id: str = Field(..., description="Business order ID")
    status: str = Field(..., description="Target status, e.g., SHIPPED, COMPLETED")

    @field_validator("order_id", "status", mode="before")
    @classmethod
    def clean_strings(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("Field cannot be empty")
        return v


class BatchOrderQueryRequest(BaseModel):
    order_ids: List[str] = Field(..., min_length=1, description="List of business order IDs to query")

    @field_validator("order_ids", mode="before")
    @classmethod
    def clean_list(cls, v):
        if isinstance(v, list):
            if not v or any(not isinstance(i, str) or not i.strip() for i in v):
                raise ValueError("order_ids list cannot contain empty strings")
        return v




# ==========================================
# Response Schemas (Master-Detail Aggregate)
# ==========================================
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    price: float
    quantity: int


class PaymentItemResponse(BaseModel):
    id: int
    payment_amount: float
    payment_method: str
    status: str
    transaction_id: Optional[str] = None
    paid_at: Optional[datetime] = None


class OrderMasterResponse(BaseModel):
    id: int
    order_id: str
    user_id: int
    total_amount: float
    status: str
    created_at: Optional[datetime] = None


class OrderDetailResponse(BaseModel):
    order: OrderMasterResponse
    items: List[OrderItemResponse]
    payments: List[PaymentItemResponse]