# @Author: Sheep Wang
# @File: main.py
# @Created: 2026-08-05 23:23
# @Description: main.py


import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.login_api import router as login_router
from api.register_api import router as register_router
from api.products_api import router as products_router
from api.orders_api import router as orders_router
from api.payment_api import router as payment_router
from utils.exception_handlers import register_exception_handlers




# Initialize FastAPI application with Swagger metadata
app = FastAPI(
    title="E-Commerce Management API Hub",
    description="""
    ## E-Commerce Backend Management API Documentation
    
    This Interactive API documentation provides endpoints for:
    * **Authentication**: User Registration, Login, and JWT Bearer Authentication.
    * **Product Management**: Product Browsing and CRUD operations.
    * **Order Management**: Order Creation, Order Details, and Inventory Lock.
    * **Payment Management**: Payment Processing and Status Updates.
    """,
    version="1.0.0",
    docs_url="/docs",      # Interactive Swagger UI route
    redoc_url="/redoc"     # Alternative ReDoc documentation route
)

#==================Global Exception Handler==========================
register_exception_handlers(app)



"""
Configure Cross-Origin Resource Sharing (CORS) — 
essential for production environments and decoupled frontend-backend architectures
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                            # Allows access from all frontend domains — can be replaced with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



# Register routes
app.include_router(register_router, prefix="/api/v1", tags=["User Authentication"])
app.include_router(login_router, prefix="/api/v1", tags=["User Authentication"])
app.include_router(products_router, prefix="/api/v1", tags=["Product Management"])
app.include_router(orders_router, prefix="/api/v1", tags=["Order Management"])
app.include_router(payment_router, prefix="/api/v1", tags=["Payment Management"])


# Health check endpoint at the root path
@app.get("/", tags=["health check"])
def health_check():
    """
    Service health check endpoint used by monitoring systems or load balancers
    to verify that the FastAPI application is alive and responsive.
    """
    return {
        "status": "healthy",
        "service": "E-Commerce Management API",
        "message": "Service is running normally."
    }


# loc entering
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)






# Collect all router
# routers = [login_router, register, products]


# #Mapping all router
# for router in routers:
#     app.include_router(router)


# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host="127.0.0.1",
#         port=8000,
#         reload=False
#     )