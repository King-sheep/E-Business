# @Author: Sheep Wang
# @File: payment_model.py
# @Created: 2026-09-06 22:51
# @Description: payment_model.py


from pydantic import BaseModel, Field, field_validator
from typing import Optional




class PaymentCreateRequest(BaseModel):
    order_id: str = Field(..., description="Business order ID, e.g., ORDxxx")
    payment_method: str = Field(..., description="Payment method, e.g., CREDIT_CARD, ALIPAY, WECHAT")
    payment_amount: float = Field(..., gt=0, description="Actual payment amount")

    @field_validator("order_id", "payment_method", mode="before")
    @classmethod
    def clean_strings(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("Field cannot be empty")
        return v


class PaymentQueryRequest(BaseModel):
    order_id: str = Field(..., description="Business order ID")

    @field_validator("order_id", mode="before")
    @classmethod
    def clean_string(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("order_id cannot be empty")
        return v