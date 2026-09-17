# @Author: Sheep Wang
# @File: products_model.py
# @Created: 2026-09-03 22:32
# @Description: products_model.py


from pydantic import BaseModel, BeforeValidator
from typing import Optional, List, Annotated, Any




# 1. Define a centralized helper function to clean empty strings/lists into None
def convert_empty_to_none(v: Any) -> Any:
    if isinstance(v, str) and v.strip() == "":
        return None
    if isinstance(v, (list, dict, set)) and len(v) == 0:
        return None
    return v

# 2. Create strict typed annotated aliases for optional fields
# These keep strict types (str, float, int) for OpenAPI/IDE, but safely pre-process "" -> None
OptionalStr = Annotated[str | None, BeforeValidator(convert_empty_to_none)]
OptionalFloat = Annotated[float | None, BeforeValidator(convert_empty_to_none)]
OptionalInt = Annotated[int | None, BeforeValidator(convert_empty_to_none)]
OptionalIds = Annotated[list[int] | None, BeforeValidator(convert_empty_to_none)]


# ==========================================
# Request Models
# ==========================================

# Base Class with strict types, but safely handles empty inputs
class ProductBase(BaseModel):
    name: OptionalStr = None
    price: OptionalFloat = None
    stock: OptionalInt = None
    description: OptionalStr = None


# Request model for creating a new product (Strictly requires valid types)
class ProductCreate(ProductBase):
    name: str  # Required for creation
    price: float  # Required for creation
    stock: int = 1


# Request model for updating an existing product
class ProductsRequestUpdate(ProductBase):
    id: int


# Request model for querying products (All fields strict yet optional for full scan)
class ProductQuery(ProductBase):
    ids: OptionalIds = None


# Request Model for Deleting Products
class ProductDelete(BaseModel):
    # Use the clean annotated type to ensure ids is a list of integers, 
    # and safely handle empty inputs like [] or "" -> None
    ids: OptionalIds = None