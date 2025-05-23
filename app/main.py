from fastapi import FastAPI, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from app.api.tasks import router as tasks_router
from app.api.auth import router as auth_router
from app.db.session import engine
from app.db.base import Base
from contextlib import asynccontextmanager
import logging
import time
from typing import Callable
import traceback

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Startup: database initialization
        logger.info("Initializing database...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database successfully initialized")
        yield
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

app = FastAPI(
    title="To Do Backend",
    description="Task Management API",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "tasks",
            "description": "Task operations",
        },
        {
            "name": "auth",
            "description": "Authentication and token management operations",
        },
    ],
    lifespan=lifespan,
    # Configure OpenAPI for Bearer JWT support
    openapi_extra={
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
        "security": [{"BearerAuth": []}]
    }
)

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"Method: {request.method} Path: {request.url.path} "
            f"Status: {response.status_code} Duration: {process_time:.2f}s"
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Error processing request: {request.method} {request.url.path} "
            f"Duration: {process_time:.2f}s Error: {str(e)}"
        )
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TrustedHost configuration
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Replace with specific hosts in production
)

app.include_router(tasks_router)
app.include_router(auth_router)

# Define security scheme for Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


