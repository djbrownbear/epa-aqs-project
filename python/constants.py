import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CONNECTION_TYPE = os.getenv("DB_CONNECTION_TYPE", "mysql")
MODE = os.getenv("MODE", "development").lower() # "development" or "production"
MAX_INPUT_LENGTH = 1000
BLOCKED_PATTERNS = ["ignore", "disregard", "forget", "repeat back", "show me the prompt", "new instructions", "override", "pretend", "bypass","you are now", "system message","system:", "assistant:", "user:", "reset"]