# @Author: Sheep Wang
# @File: products_model.py
# @Created: 2026-09-03 22:32
# @Description: products_model.py


from pydantic import BaseModel, BeforeValidator, Field
from typing import Optional, List, Annotated, Any




# Define a centralized helper function to clean empty strings/lists into None
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

# 1. Base Class now uses safe optional types with empty-string converter
class ProductBase(BaseModel):
    """Base model for product containing flexible optional fields."""
    name: OptionalStr = None
    price: OptionalFloat = None
    stock: OptionalInt = None
    description: OptionalStr = None


# 2. For create/update, you can inherit or explicitly enforce strict required fields
class ProductCreate(BaseModel):
    """Request model for creating a new product (Strictly required fields)."""
    name: str = Field(..., min_length=1, description="Product name cannot be empty")
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    stock: int = Field(..., ge=0, description="Stock cannot be negative")
    description: str = Field(..., min_length=1, description="Description cannot be empty")


class ProductsRequestUpdate(ProductCreate):
    """Request model for updating an existing product."""
    id: int = Field(..., description="Product ID is required for update")


# 3. Query model inherits from ProductBase, perfectly supporting empty strings -> None
class ProductQuery(ProductBase):
    """Request model for querying products (All fields optional for full scan)."""
    ids: OptionalIds = None


# Request Model for Deleting Products
class ProductDelete(BaseModel):
    # Use the clean annotated type to ensure ids is a list of integers, 
    # and safely handle empty inputs like [] or "" -> None
    ids: OptionalIds = None