import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
SHEET_NAME = os.getenv('SHEET_NAME')
WORKSHEET_NAME = os.getenv('WORKSHEET_NAME')
