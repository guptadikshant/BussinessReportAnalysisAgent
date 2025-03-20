import sys
from loguru import logger
import os
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_groq.chat_models import ChatGroq
import logging

# Remove default logger
logger.remove()
# Add custom configuration
logger.add(
    sys.stdout,
    level="INFO",
    filter=lambda record: not any(
        term in record["message"] 
        for term in [
            "HTTP Request:", 
            "HTTP Response:", 
            "api.groq.com", 
            "generativelanguage.googleapis.com",
            "POST https://", 
            "GET https://",
            "200 OK"
        ]
    )
)

# Add at the top of your file after imports
os.environ["LANGCHAIN_VERBOSE"] = "false"

# Disable LangChain logging
logging.getLogger("langchain").setLevel(logging.ERROR)
logging.getLogger("langchain_google_genai").setLevel(logging.ERROR)
logging.getLogger("langchain_groq").setLevel(logging.ERROR)

class LLMModel:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_gemini_model(
        model_name: str, temperature: int
    ) -> ChatGoogleGenerativeAI:
        logger.debug(
            f"Getting {model_name} gemini model with temperature: {temperature}"
        )
        gemini_model = ChatGoogleGenerativeAI(
            api_key=os.environ["GOOGLE_API_KEY"],
            model=model_name,
            temperature=temperature,
        )
        logger.debug(
            f"Successfully get {model_name} gemini model with temperature: {temperature}"
        )
        return gemini_model

    @staticmethod
    def get_groq_model(model_name: str, temperature: str) -> ChatGroq:
        logger.debug(f"Getting {model_name} groq model with temperature: {temperature}")
        groq_model = ChatGroq(
            api_key=os.environ["GROQ_API_KEY"],
            model=model_name,
            temperature=temperature,
        )
        logger.debug(
            f"Successfully get {model_name} groq model with temperature: {temperature}"
        )
        return groq_model
