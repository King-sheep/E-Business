# @Author: Sheep Wang
# @File: products.py
# @Created: 2026-09-02 22:06
# @Description: products_api.py



from fastapi import APIRouter, Depends
from model.products_model import ProductCreate, ProductsRequestUpdate, ProductQuery, ProductDelete
from service.products_service import ProductsService
from utils.response import BaseResponse
from utils.auth import get_current_user
from utils.logger import logger





# Create a products router
router = APIRouter(prefix="/products", tags=["products management"])




# 1. Select products(Allow to public)
@router.post("/query", response_model=BaseResponse)
def query_products_api(query: ProductQuery):
    """
    **Query Product List**:
    - Filter products based on search criteria such as name or category.
    - Public endpoint (No JWT Token required).
    """
    logger.info(f"API Request: Querying products with criteria: {query}")
    res = ProductsService.get_product(query)
    logger.info("API Response: Product query executed successfully.")
    return res


# 2. Create new products
@router.post("/add", response_model=BaseResponse)
def create_product_api(
    data: ProductCreate,
    current_user: str = Depends(get_current_user) #<-- validate token 
):
    """
    **Create New Product**:
    - Adds a new product item to the catalog.
    - **Requires JWT Bearer Token** in Authorization header.
    """
    logger.info(f"API Request: Create product requested by user: {current_user}")
    res = ProductsService.add_product(data)
    logger.info("API Response: Create product process completed.")
    return res


# 3.Update product
@router.put("/update", response_model=BaseResponse)
def update_product_api(
    data: ProductsRequestUpdate,
    current_user: str = Depends(get_current_user)
):
    """
    **Update Product Details**:
    - Modifies existing product information.
    - **Requires JWT Bearer Token** in Authorization header.
    """
    logger.info(f"API Request: Update product requested by user: {current_user}")
    res = ProductsService.modify_product(data)
    logger.info("API Response: Update product process completed.")
    return res


# 4. Delete product
@router.delete("/del", response_model=BaseResponse)
def delete_products_api(
    body: ProductDelete,  # 改为接收 ProductDelete 模型对象
    current_user: str = Depends(get_current_user)
):
    """
    **Batch Delete Products**:
    - Deletes one or multiple products by their unique IDs.
    - **Requires JWT Bearer Token** in Authorization header.
    """
    # Defensive check: Ensure IDs are provided after model pre-validation
    if not body.ids:
        return BaseResponse(code=400, msg="Product IDs list cannot be empty", data=None)

    logger.info(f"API Request: Batch delete products with IDs {body.ids} requested by user: {current_user}")
    
    # Pass clean list[int] to service layer
    res = ProductsService.del_product(body.ids)
    
    logger.info(f"API Response: Batch delete completed for IDs {body.ids}.")
    return res