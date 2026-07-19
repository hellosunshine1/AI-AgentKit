"""
run backend server.
"""

import asyncio
import sys

import uvicorn
from dotenv import load_dotenv

from app.core.config import settings

load_dotenv()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.is_dev())
