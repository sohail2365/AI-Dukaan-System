# whatsapp.py — WhatsApp messaging for Dukaan AI
#
# Do modes:
#   1. FREE (default): wa.me links banata hai — frontend pe button dabao,
#      WhatsApp khulta hai pre-filled message ke saath. Koi API nahi chahiye.
#   2. AUTO (optional): agar .env mein WHATSAPP_TOKEN aur WHATSAPP_PHONE_ID
#      set hain (Meta WhatsApp Cloud API), toh message automatically bhejta hai.
#
# Cloud API setup (optional, baad mein): developers.facebook.com → WhatsApp → Cloud API

import os
import re
import json
import urllib.parse
import urllib.request

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v20.0")

AUTO_SEND_ENABLED = bool(WHATSAPP_TOKEN and WHATSAPP_PHONE_ID)


# ---------- Phone normalization (Pakistan) ----------
def normalize_phone(phone: str):
    """03001234567 / +92 300 1234567 / 3001234567 → 923001234567
    Returns None agar phone invalid ya 'unknown' hai."""
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if not digits:
        return None
    if digits.startswith("0092"):
        digits = digits[2:]
    if digits.startswith("92") and len(digits) == 12:
        return digits
    if digits.startswith("0") and len(digits) == 11:
        return "92" + digits[1:]
    if digits.startswith("3") and len(digits) == 10:
        return "92" + digits
    # International ya unknown format — 11+ digits ho toh as-is try karo
    if len(digits) >= 11:
        return digits
    return None


def fmt_rs(amount) -> str:
    """1540.0 → '1,540' — .00 hatao, comma lagao."""
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return str(amount)
    if amount == int(amount):
        return f"{int(amount):,}"
    return f"{amount:,.2f}"


def _baaki_line(total_baaki) -> str:
    try:
        b = float(total_baaki)
    except (TypeError, ValueError):
        return f"Aapka baaki: Rs. {fmt_rs(total_baaki)}"
    if b > 0:
        return f"Aapka kul baaki: Rs. {fmt_rs(b)}"
    if b < 0:
        return f"Aapka credit (dukaan par): Rs. {fmt_rs(-b)}"
    return "Aapka baaki safai hai — shukriya!"


# ---------- Message templates (Roman Urdu) ----------
def compose_entry_receipt(shop_name: str, customer_name: str,
                          items: list, grand_total, total_baaki) -> str:
    """items = [{'item': ..., 'quantity': ..., 'price': ..., 'total': ...}, ...]"""
    lines = [f"*{shop_name}*", f"Salam {customer_name.title()}!", "", "Aaj ki entry:"]
    for i in items:
        qty = i.get("quantity", 1)
        qty_str = int(qty) if float(qty) == int(qty) else qty
        lines.append(
            f"- {str(i.get('item', '')).title()} x{qty_str} @ Rs.{fmt_rs(i.get('price', 0))} = Rs.{fmt_rs(i.get('total', 0))}"
        )
    lines += [
        "",
        f"Total: Rs. {fmt_rs(grand_total)}",
        _baaki_line(total_baaki),
        "",
        "Shukriya!",
    ]
    return "\n".join(lines)


def compose_payment_receipt(shop_name: str, customer_name: str,
                            amount, total_baaki) -> str:
    return "\n".join([
        f"*{shop_name}*",
        f"Salam {customer_name.title()}!",
        "",
        f"Aapki payment Rs. {fmt_rs(amount)} mil gayi hai.",
        _baaki_line(total_baaki),
        "",
        "Shukriya!",
    ])


def compose_reminder(shop_name: str, customer_name: str, total_baaki) -> str:
    try:
        b = float(total_baaki)
    except (TypeError, ValueError):
        b = 0
    if b <= 0:
        # Koi baaki nahi — reminder ka faida nahi
        return "\n".join([
            f"*{shop_name}*",
            f"Salam {customer_name.title()}!",
            "",
            "Aapka koi baaki nahi hai. Shukriya!",
        ])
    return "\n".join([
        f"*{shop_name}*",
        f"Salam {customer_name.title()}!",
        "",
        f"Yaad dehani: aapka baaki Rs. {fmt_rs(b)} hai.",
        "Jab aasani ho, ada kar dein.",
        "",
        "Shukriya!",
    ])


# ---------- Link + send ----------
def make_wa_link(phone: str, message: str):
    """wa.me click-to-chat link. Phone None ho toh sirf share-text link."""
    encoded = urllib.parse.quote(message)
    normalized = normalize_phone(phone) if phone else None
    if normalized:
        return f"https://wa.me/{normalized}?text={encoded}"
    return f"https://wa.me/?text={encoded}"


def send_via_cloud_api(phone: str, message: str) -> dict:
    """Meta WhatsApp Cloud API se direct message. Sirf tab chalta hai jab
    WHATSAPP_TOKEN + WHATSAPP_PHONE_ID .env mein set hon."""
    if not AUTO_SEND_ENABLED:
        return {"sent": False, "reason": "Cloud API configured nahi hai"}
    normalized = normalize_phone(phone)
    if not normalized:
        return {"sent": False, "reason": f"Phone number invalid: {phone}"}

    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_ID}/messages"
    payload = json.dumps({
        "messaging_product": "whatsapp",
        "to": normalized,
        "type": "text",
        "text": {"body": message},
    }).encode()
    req = urllib.request.Request(
        url, data=payload, method="POST",
        headers={
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode())
        return {"sent": True, "response": body}
    except Exception as e:
        return {"sent": False, "reason": str(e)}


def build_whatsapp_payload(phone: str, message: str, auto_send: bool = True) -> dict:
    """Ek hi jagah se: link banao + (agar configured ho) auto-send karo.
    Frontend ko yeh object milta hai — link hamesha hota hai fallback ke liye."""
    result = {
        "message": message,
        "link": make_wa_link(phone, message),
        "phone_valid": normalize_phone(phone) is not None,
        "auto_sent": False,
    }
    if auto_send and AUTO_SEND_ENABLED and result["phone_valid"]:
        sent = send_via_cloud_api(phone, message)
        result["auto_sent"] = sent.get("sent", False)
        if not result["auto_sent"]:
            result["auto_send_error"] = sent.get("reason", "")
    return result
