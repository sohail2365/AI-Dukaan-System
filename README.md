# 🏪 Dukaan AI — Smart Karyana Shop Manager

AI-powered shop management system for Pakistani Karyana stores.
Natural language input in Urdu/English — no training required.

## Features
- 🤖 AI parses Urdu/English input naturally
- 📦 Auto price fetch from Google Sheets inventory
- 👥 Customer khaata management with net balance
- 💰 Payment tracking — udhaar aur wasool
- 🛒 Purchase tracking with supplier records
- 📊 Stock auto-update on every sale/purchase
- ✏️ Full edit/delete on all records
- 🧮 Built-in calculator
- 🌐 Web UI + REST API

## Tech Stack
Python · FastAPI · Groq LLaMA 3.3 · SQLite · Google Sheets API · HTML/CSS/JS

## Project Structure
- `ai_parser.py` — Natural language parsing
- `server.py` — FastAPI REST API
- `customers.py` — Customer & khaata logic
- `inventory.py` — Google Sheets integration
- `database.py` — SQLite setup
- `config.py` — Settings & constants
- `main.py` — CLI interface
- `index.html` — Web UI

## Built by
Sohail — Karyana shop owner, self-taught AI Engineer
