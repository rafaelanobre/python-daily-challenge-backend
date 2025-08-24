from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from clerk_backend_api import Clerk
import os

from .routes import challenge
from .logger import get_logger

clerk_sdk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

logger = get_logger()
logger.info("Starting Python Daily Challenge API")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(challenge.router, prefix="/api")
