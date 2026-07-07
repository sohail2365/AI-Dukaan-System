# Dukaan AI

Ek AI-powered Karyana shop management system — Urdu/Roman Urdu mein natural language se entries, khaata, inventory, purchases, aur ab WhatsApp reminders bhi.

## Features

**Sales & Khaata**
- Natural language entry (Urdu/English/Roman Urdu): "Ali ne surf excel 2 liya 200 mein"
- Multi-item entries + printable bill
- Payment tracking (udhaar wapasi)
- Per-customer khaata view + edit/delete

**Inventory**
- Item CRUD with sale price, purchase rate, stock, reorder level
- Auto stock decrement on sale, auto increment on purchase
- Variant matching (e.g. "coke" → "coke 1.5L" / "coke 500ml")
- Google Sheets se bulk import (`import_sheet.py`)

**Purchases**
- Supplier + item + quantity + rate/total tracking
- Auto rate divide (agar total diya ho quantity se)
- Full purchase history

**WhatsApp integration** (naya)
- Har sale/payment ke baad customer ko receipt bhejne ka option
- Bulk reminders: sab customers jinke baaki hai unhe ek jagah se WhatsApp
- Two modes:
  - **Free (default):** wa.me links banate hain — button dabao, WhatsApp pre-filled message ke saath khulta hai
  - **Auto (optional):** Meta WhatsApp Cloud API se direct send (setup neeche)

**Reports & Backup**
- Dashboard: aaj/mahine ki sale, payments, purchases, total baaki, top baaki wale, low stock
- CSV export: customers, khaata, inventory

**Multi-tenant + Auth**
- Har shop ka apna data isolated
- JWT auth, password reset via shop identity verification

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
```

`.env` file banao (ye git mein commit nahi hoti):

```
GROQ_API_KEY=your_groq_key_here
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=some-random-long-string
```

Chalao:

```bash
uvicorn server:app --reload
```

Browser: `http://localhost:8000/ui`

### Google Sheets import (optional)

`credentials.json` (Google Service Account) same folder mein rakho, phir:

```bash
python import_sheet.py
```

### WhatsApp Cloud API (optional — auto-send ke liye)

Free mode default hai (wa.me links). Auto-send chahiye toh Meta Business par app banao:

1. https://developers.facebook.com → My Apps → Create App → Business
2. WhatsApp product add karo → Cloud API section
3. Test phone number aur access token milega
4. `.env` mein add karo:
   ```
   WHATSAPP_TOKEN=EAAG...your_token
   WHATSAPP_PHONE_ID=1234567890
   ```
5. Server restart karo — ab har entry pe message automatically customer ko chala jayega

**Note:** Cloud API free tier: 1000 conversations/month. Test number pe pehle sirf pre-registered numbers hi message receive kar sakte hain — production ke liye phone number verification karni padegi.

## Deployment (Vercel)

`vercel.json` already configured hai. Environment variables Vercel dashboard mein add karo (GROQ_API_KEY, DATABASE_URL, SECRET_KEY, aur agar WhatsApp use kar rahe ho toh WHATSAPP_TOKEN + WHATSAPP_PHONE_ID). Deploy:

```bash
vercel --prod
```

## API Endpoints

- `POST /auth/register`, `/auth/login`, `/auth/reset-password`
- `POST /entry/parse`, `/entry/save`, `PUT /entry/edit`, `DELETE /entry/{id}`
- `POST /entry/multi/parse`, `/entry/multi/save`
- `GET /khaata/{name}`, `GET /customers/all`
- `POST /customer/add`, `PUT /customer/edit`, `DELETE /customer/{name}`
- `GET /inventory/all`, `POST /inventory/add`, `PUT /inventory/edit`, `DELETE /inventory/item/{id}`
- `POST /purchase/parse`, `/purchase/save`, `PUT /purchase/edit`, `DELETE /purchase/{id}`, `GET /purchases/all`
- `POST /whatsapp/reminder`, `/whatsapp/bulk-reminders` **(naya)**
- `GET /reports/dashboard` **(naya)**
- `GET /export/{customers|khaata|inventory}` **(naya)**
