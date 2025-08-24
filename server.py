from src.logger import setup_logger
import os

if __name__ == "__main__":
    import uvicorn

    setup_logger()

    environment = os.getenv("ENVIRONMENT", "development").lower()
    is_dev = environment == "development"

    if is_dev:
        uvicorn.run(
            "src.app:app",
            host="0.0.0.0",
            port=8000,
            log_config=None,
            access_log=True,
            reload=True
        )
    else:
        from src.app import app
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_config=None,
            access_log=True,
            reload=False
        )
