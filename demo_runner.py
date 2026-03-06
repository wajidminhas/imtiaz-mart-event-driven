#!/usr/bin/env python3
"""
Imtiaz Mart - Safe Demo Runner
✅ Uses exact JSON schemas from YOUR Swagger UI
✅ Dynamically captures IDs (no hardcoded values)
✅ Pauses for Video Recording
"""
import requests
import time
import json
import sys

# 🎨 Colors
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

# ⚙️ Configuration
BASE_URL = "http://localhost"
SERVICES = {
    "user": 8000,
    "product": 8001,
    "payment": 8002,
    "order": 8003,
    "inventory": 8004
}

# 📝 PAYLOADS (YOUR EXACT SCHEMA - Only Fixed Python Syntax)
# ✅ Changed: true → True (Python syntax)
# ✅ Added: timestamp for unique values (avoid duplicates)
timestamp = int(time.time())

PAYLOADS = {
    "user": {
        "email": f"user_{timestamp}@example.com",
        "username": f"user_{timestamp}",
        "password": "stringst",  # ✅ YOUR schema (8 chars minimum)
        "first_name": "Demo",
        "last_name": "Client"
    },
    "product": {
        "name": f"Demo Laptop {timestamp}",
        "description": "Test product for demo video",
        "price": 1000,
        "stock_quantity": 5,
        "is_active": True  # ✅ Fixed: true → True (Python syntax)
    },
    # IDs will be injected dynamically before sending
    "order": {
        "user_id": 0,  # Will be updated dynamically
        "shipping_address": "123 Demo Street",
        "notes": "Demo order",
        "items": [
            {
                "product_id": 0,  # Will be updated dynamically
                "quantity": 1
            }
        ]
    },
    "payment": {
        "order_id": 0,  # Will be updated dynamically
        "user_id": 0,
        "amount": 1000,
        "currency": "PKR",
        "payment_method": "payfast",
        "payment_provider": "payfast",
        "provider_transaction_id": f"txn_{timestamp}",
        "provider_payment_id": f"pay_{timestamp}",
        "description": "Demo payment",
        "payment_metadata": "demo"
    }
}

def print_step(msg):
    print(f"\n{BLUE}{'='*40}{NC}")
    print(f"{BLUE}🚀 {msg}{NC}")
    print(f"{BLUE}{'='*40}{NC}")

def extract_id(response_json):
    """Handles both {'id': 1} and {'data': {'id': 1}} structures"""
    if isinstance(response_json, dict):
        if "id" in response_json:
            return response_json["id"]
        if "data" in response_json and isinstance(response_json["data"], dict):
            return response_json["data"].get("id")
    return None

def main():
    print_step("Starting Imtiaz Mart Event-Driven Demo")
    
    # 1️⃣ Register User
    print_step("1️⃣ Registering User...")
    try:
        res = requests.post(
            f"{BASE_URL}:{SERVICES['user']}/users/register",
            json=PAYLOADS["user"],
            timeout=10
        )
        if res.status_code not in [200, 201]:
            print(f"{NC}❌ Failed: {res.status_code} - {res.text}{NC}")
            return
        user_id = extract_id(res.json())
        print(f"{GREEN}✅ User Created (ID: {user_id}){NC}")
        print(f"{YELLOW}⏸️  Pause for video (3 seconds)...{NC}")
        time.sleep(3)
    except Exception as e:
        print(f"{NC}❌ Error: {e}{NC}")
        return

    # 2️⃣ Create Product
    print_step("2️⃣ Creating Product...")
    try:
        res = requests.post(
            f"{BASE_URL}:{SERVICES['product']}/products/",
            json=PAYLOADS["product"],
            timeout=10
        )
        if res.status_code not in [200, 201]:
            print(f"{NC}❌ Failed: {res.status_code} - {res.text}{NC}")
            return
        product_id = extract_id(res.json())
        print(f"{GREEN}✅ Product Created (ID: {product_id}){NC}")
        print(f"{YELLOW}⏸️  Pause for video (3 seconds)...{NC}")
        time.sleep(3)
    except Exception as e:
        print(f"{NC}❌ Error: {e}{NC}")
        return

    # 3️⃣ Place Order (Inject Dynamic IDs)
    print_step("3️⃣ Placing Order...")
    try:
        PAYLOADS["order"]["user_id"] = user_id
        PAYLOADS["order"]["items"][0]["product_id"] = product_id
        
        res = requests.post(
            f"{BASE_URL}:{SERVICES['order']}/orders/",
            json=PAYLOADS["order"],
            timeout=10
        )
        if res.status_code not in [200, 201]:
            print(f"{NC}❌ Failed: {res.status_code} - {res.text}{NC}")
            return
        order_id = extract_id(res.json())
        print(f"{GREEN}✅ Order Created (ID: {order_id}){NC}")
        print(f"{YELLOW}⏸️  Pause for video (3 seconds)...{NC}")
        time.sleep(3)
    except Exception as e:
        print(f"{NC}❌ Error: {e}{NC}")
        return

    # 4️⃣ Process Payment (Inject Dynamic ID)
    print_step("4️⃣ Processing Payment...")
    try:
        PAYLOADS["payment"]["order_id"] = order_id
        PAYLOADS["payment"]["user_id"] = user_id
        
        res = requests.post(
            f"{BASE_URL}:{SERVICES['payment']}/payments/",
            json=PAYLOADS["payment"],
            timeout=10
        )
        if res.status_code not in [200, 201]:
            print(f"{NC}❌ Failed: {res.status_code} - {res.text}{NC}")
            return
        print(f"{GREEN}✅ Payment Successful!{NC}")
        print(f"{YELLOW}⏸️  Pause for video (3 seconds)...{NC}")
        time.sleep(3)
    except Exception as e:
        print(f"{NC}❌ Error: {e}{NC}")
        return

    print_step("✅ Demo Complete! Check Kafka UI for Events.")
    print(f"{GREEN}🎬 Ready for recording!{NC}")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print(f"{NC}❌ Please install requests: pip install requests{NC}")
        sys.exit(1)
    
    main()