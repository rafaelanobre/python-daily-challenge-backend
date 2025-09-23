from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import challenge, webhooks
from .logger import get_logger
from .core.config import settings

logger = get_logger()
logger.info("Starting Python Daily Challenge API")

app = FastAPI()

if not settings.allowed_origins:
    raise ValueError("ALLOWED_ORIGINS for environment not set")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(','),
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization', 'Accept', 'Origin', 'X-Requested-With']
)

app.include_router(challenge.router, prefix="/api")
app.include_router(webhooks.router, prefix="/webhooks")
