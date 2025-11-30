import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    REDIS_CONN_STRING = os.getenv("REDIS_CONNECTION_STRING", "redis://localhost:6379/0")
    
    # Data settings
    DATA_DIR = os.path.join(os.getcwd(), 'data', '*.json')

def setup_logging():
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )