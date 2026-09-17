# @Author: Sheep Wang
# @File: exception_handlers.py
# @Created: 2026-09-14 23:16
# @Description: exception_handlers.py


from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from utils.response import BaseResponse





def register_exception_handlers(app):
    """
    Register global exception handlers for the FastAPI application.
    """
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Capture Pydantic validation errors (HTTP 422) and convert them 
        into the unified BaseResponse format.
        """
        errors = exc.errors()
        if errors:
            err = errors[0]
            field = " -> ".join(str(x) for x in err["loc"])
            msg = f"Field error: {field} {err['msg']}"
        else:
            msg = "Invalid request parameters"

        # Wrap in the global standard response model
        custom_response = BaseResponse(
            code=422,
            msg=msg,
            data=None
        )
        
        return JSONResponse(
            status_code=200,  # Return HTTP 200 with business code 422, or change to 422 if needed
            content=custom_response.model_dump()
        )