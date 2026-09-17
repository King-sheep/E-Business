# @Author: Sheep Wang
# @File: register_service.py
# @Created: 2026-08-09 22:07
# @Description: register_service.py


from DAO.register_DAO import RegisterDAO
from model.register_model import RegisterRequest
from utils.logger import logger



class RegisterService:

    @staticmethod
    def register_user(data: RegisterRequest) -> dict:
        logger.info(f"Service: Starting registration process for username: '{data.username}'")
        # Check username if exists
        existing_user = RegisterDAO.get_user_by_name(data.username)
        if existing_user:
            logger.warning(f"Service: Registration failed - Username '{data.username}' already exists.")
            return {
                "success": False,
                "code": 400,
                "msg": f"username '{data.username}' is exist, pls choose another username",
                "data": None
            }


        # Run sql to insert data into DB
        logger.warning(f"Service: Registration failed - Username '{data.username}' already exists.")
        new_user_id = RegisterDAO.create_new_user(data)

        return {
            "success": True,
            "code": 200,
            "msg": "Registration successful",
            "data": {"user_id": new_user_id, "username": data.username}

        }