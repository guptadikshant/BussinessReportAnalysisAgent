import sys
from loguru import logger
from fastapi import FastAPI

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

