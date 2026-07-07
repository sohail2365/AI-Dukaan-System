# main.py
from database import setup_database
from ai_parser import parse_entry
from customers import add_khaata_entry, show_customer_khaata, add_customer
from inventory import get_item_price

def handle_new_entry():
    entry = input("\nLikho (jaise: Ali ne 2 Surf Excel liya): ").strip()
    if not entry:
        return

    data = parse_entry(entry)
    if not data:
        return

    print(f"🤖 AI ne samjha: {data}")

    # Customer missing
    if not data.get("customer"):
        data["customer"] = input("👤 Customer naam? ").strip()

    # Item missing
    if not data.get("item"):
        data["item"] = input("📦 Item naam? ").strip()

    # Price — sheets se lo
    if not data.get("price"):
        sheet_item = get_item_price(data["item"])
        if sheet_item:
            print(f"📦 Sheets se mila: {sheet_item['name']} — Rs. {sheet_item['price']}")
            if sheet_item["stock"] == 0:
                print(f"⚠️  Warning: {sheet_item['name']} out of stock hai!")
            data["price"] = sheet_item["price"]
        else:
            data["price"] = float(input(f"💰 {data['item']} ka price? Rs. "))

    total = round(data["quantity"] * data["price"], 2)
    confirm = input(f"\nConfirm: {data['customer'].title()} — {data['item']} x{data['quantity']} — Rs.{total}? (y/n): ")

    if confirm.lower() == "y":
        add_khaata_entry(data["customer"], data["item"], data["quantity"], data["price"])

def main():
    setup_database()

    while True:
        print("\n" + "="*40)
        print("   🏪 DUKAAN AI — Karyana Manager")
        print("="*40)
        print("  1 — Naya khaata entry")
        print("  2 — Customer ka khaata dekho")
        print("  3 — Naya customer add karo")
        print("  4 — Bahir jao")
        print("="*40)

        choice = input("Choice: ").strip()

        if choice == "1":
            handle_new_entry()
        elif choice == "2":
            name = input("👤 Customer naam: ").strip()
            show_customer_khaata(name)
        elif choice == "3":
            name = input("👤 Customer naam: ").strip()
            phone = input("📞 Phone number: ").strip()
            add_customer(name, phone)
        elif choice == "4":
            print("\nAllah Hafiz! 👋")
            break
        else:
            print("❌ Galat choice — 1 to 4 mein se chunо")

if __name__ == "__main__":
    main()