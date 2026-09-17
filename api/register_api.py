# @Author: Sheep Wang
# @File: register_api.py
# @Created: 2026-08-09 21:27
# @Description: register_api.py


from fastapi import APIRouter
from model.register_model import RegisterRequest
from service.register_service import RegisterService
from utils.response import BaseResponse
from utils.logger import logger




# Create router for register
router = APIRouter()




# Call register service
@router.post("/register", response_model=BaseResponse)
def register_api(data:RegisterRequest):
    logger.info(f"API Request: User registration attempt for username: {data.username}")
    # 1.Pydantic validates parameters automatically, invalid input is rejected before reaching this point

    # 2.Import Service layer
    result = RegisterService.register_user(data)
    logger.info(f"API Response: Registration completed for username: {data.username}")
    
    # Assemble the BaseReponse structure based on business logic result
    if not result["success"]:
        return BaseResponse(
            code=result["code"], msg=result["msg"], data=None
        )

    return BaseResponse(
        code=200, msg=result.get("msg", "success"), data=result.get("data")
    )