# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Database
DB_NAME = "dukaan.db"

# Google Sheets
SHEET_ID = "1FBOBFMsmygArr5HjpPUdpA6taAoKK8KBIr0EgGy2rnw"
CREDENTIALS_FILE = "credentials.json"

# AI Model
AI_MODEL = "llama-3.3-70b-versatile"

# Validation
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY missing — .env file check karo")