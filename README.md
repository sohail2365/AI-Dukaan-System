# Dukaan AI

Ek AI-powered Karyana shop management system — Urdu/Roman Urdu mein natural language se entries, khaata, inventory, purchases, WhatsApp reminders, aur ab foundation-level SaaS features.

## Features

**Sales & Khaata**
- Natural language entry (Urdu/English/Roman Urdu)
- Multi-item entries + printable bill
- Payment tracking (udhaar wapasi)
- Per-customer khaata view + edit/soft-delete

**Inventory**
- Item CRUD with sale price, purchase rate, stock, reorder level
- Auto stock decrement on sale, auto increment on purchase
- Variant matching
- Google Sheets import (`import_sheet.py`)

**Purchases**
- Supplier + item + rate/total tracking
- Full purchase history

**WhatsApp integration**
- Har entry/payment ke baad customer ko receipt
- Bulk reminders for all defaulters
- Phone missing? Dialog se on-the-fly save + WhatsApp
- Two modes: Free (wa.me links) ya Auto-send (Meta Cloud API)

**Reports & Backup**
- Dashboard: aaj/mahine ki sale, payments, purchases, total baaki, top defaulters, low stock
- CSV export: customers, khaata, inventory
- Full backup script (JSON/CSV, per-shop)

**Foundation / Reliability**
- **Soft delete + Trash page** — deleted entries 30 days recoverable
- **Search + filter** in customers list (name/phone, baaki-only, multi-sort)
- **Rate limiting** on auth endpoints (login: 10/min, register: 5/hr, reset: 3/hr)
- **Server-side validation** with friendly Roman Urdu error messages
- **Structured logging** for production debugging
- **Multi-tenant isolation** — har shop ka data completely separate
- **Non-destructive DB migrations** — schema updates safely without data loss

**Auth**
- JWT-based, per-shop
- Password reset via shop identity verification

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
```

`.env.example` ko `.env` mein copy karo aur values fill karo:

```bash
cp .env.example .env
```

Chalao:

```bash
uvicorn server:app --reload
```

Browser: `http://localhost:8000/ui`

### WhatsApp Cloud API (optional — auto-send ke liye)

Free mode default hai (wa.me links). Auto-send ke liye Meta Business setup:

1. https://developers.facebook.com → My Apps → Create App → Business
2. WhatsApp product add → Cloud API
3. `.env` mein `WHATSAPP_TOKEN` + `WHATSAPP_PHONE_ID` daalo

**Free tier:** 1000 conversations/month. Production ke liye phone verification zaroori.

### Backup

Manual backup:

```bash
python backup.py                 # sab shops, JSON format
python backup.py --shop-id 1     # specific shop
python backup.py --format csv    # CSV format
```

Cron (Linux):

```
0 3 * * * cd /path/to/dukaan && python backup.py --output /var/backups/dukaan
```

Vercel Cron (add to `vercel.json`) ya external cron-job.org bhi kaam karta hai.

**Important:** Backup mein soft-deleted entries bhi hoti hain (recovery ke liye).

### Google Sheets import (optional)

`credentials.json` (Service Account) same folder mein rakho, phir:

```bash
python import_sheet.py
```

## Deployment (Vercel)

`vercel.json` already configured. Environment variables Vercel dashboard mein add karo. Deploy:

```bash
vercel --prod
```

## API Endpoints

**Auth (rate-limited)**
- `POST /auth/register` (5/hour)
- `POST /auth/login` (10/minute)
- `POST /auth/reset-password` (3/hour)

**Entries & Khaata**
- `POST /entry/parse`, `/entry/save`
- `POST /entry/multi/parse`, `/entry/multi/save`
- `PUT /entry/edit`
- `DELETE /entry/{id}` (soft delete — 30 days recoverable)
- `GET /khaata/{name}`

**Trash**
- `GET /trash/khaata` — last 30 days ki deleted entries
- `POST /trash/restore/{id}` — entry wapas
- `DELETE /trash/purge` — 30+ din purani permanently hatao

**Customers**
- `GET /customers/all`
- `POST /customer/add`, `PUT /customer/edit`, `DELETE /customer/{name}`
- `POST /customer/set-phone` — on-the-fly phone save from WhatsApp dialog

**Inventory & Purchases**
- `GET /inventory/all`, `POST /inventory/add`, `PUT /inventory/edit`, `DELETE /inventory/item/{id}`
- `POST /purchase/parse`, `/purchase/save`, `PUT /purchase/edit`, `DELETE /purchase/{id}`
- `GET /purchases/all`

**WhatsApp**
- `POST /whatsapp/reminder`
- `POST /whatsapp/bulk-reminders`

**Reports & Export**
- `GET /reports/dashboard`
- `GET /export/{customers|khaata|inventory}` (CSV)

## Roadmap (available on request)

- Voice input (Urdu Whisper STT)
- Barcode scanner support
- Thermal receipt printing (ESC/POS)
- Staff accounts + role-based permissions
- Customer WhatsApp chatbot (two-way messaging)
- AI-based sales predictions (needs 12+ months data)
