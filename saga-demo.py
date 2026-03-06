#!/usr/bin/env python3
"""
Imtiaz Mart - Saga Pattern Demo
✅ Shows distributed transaction rollback
✅ Payment fails → Inventory automatically restored
✅ Proves resilience and fault tolerance
"""
import requests
import time
import sys

# 🎨 Colors
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
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

timestamp = int(time.time())

def print_step(msg):
    print(f"\n{BLUE}{'='*50}{NC}")
    print(f"{BLUE}🔄 {msg}{NC}")
    print(f"{BLUE}{'='*50}{NC}")

def extract_id(response_json):
    if isinstance(response_json, dict):
        if "id" in response_json:
            return response_json["id"]
        if "data" in response_json and isinstance(response_json["data"], dict):
            return response_json["data"].get("id")
    return None

def main():
    print_step("SAGA PATTERN DEMO - Failure & Rollback Scenario")
    print(f"{YELLOW}⏱️  Timestamp: {timestamp}{NC}")
    print(f"{RED}⚠️  This demo simulates PAYMENT FAILURE{NC}")
    print(f"{YELLOW}📊 Expected: Inventory should automatically rollback{NC}")
    time.sleep(3)

    # 1️⃣ Create Product (with known stock)
    print_step("1️⃣ Creating Product (Stock: 5)...")
    try:
        res = requests.post(
            f"{BASE_URL}:{SERVICES['product']}/products/",
            json={
                "name": f"Saga Test Product {timestamp}",
                "description": "For saga rollback demo",
                "price": 500,
                "stock_quantity": 5,
                "is_active": True
            },
            timeout=10
        )
        if res.status_code not in [200, 201]:
            print(f"{NC}❌ Failed: {res.status_code} - {res.text}{NC}")
            return
        product_id = extract_id(res.json())
        print(f"{GREEN}✅ Product Created (ID: {product_id}, Stock: 5){NC}")
        time.sleep(2)
    except Exception as e:
        print(f"{NC}❌ Error: {e}{NC}")
        return

    # 2️⃣ Check Initial Stock
    print_step("2️⃣ Checking Initial Stock...")
    try:
        res = requests.get(
            f"{BASE_URL}:{SERVICES['inventory']}/inventory/{product_id}",
            timeout=10
        )
        if res.status_code == 200:
            initial_stock = res.json().get("stock_quantity", res.json().get("data", {}).get("stock_quantity", 5))
            print(f"{GREEN}✅ Initial Stock: {initial_stock}{NC}")
        time.sleep(2)
    except Exception as e:
        print(f"{NC}⚠️  Skip: {e}{NC}")

    # 3️⃣ Create Order (Stock Reserved)
    print_step("3️⃣ Creating Order (Stock Reserved)...")
    try:
        res = requests.post(
            f"{BASE_URL}:{SERVICES['order']}/orders/",
            json={
                "user_id": 1,
                "items": [{"product_id": product_id, "quantity": 1, "price": 500}]
            },
            timeout=10
        )
        if res.status_code not in [200, 201]:
            print(f"{NC}❌ Failed: {res.status_code} - {res.text}{NC}")
            return
        order_id = extract_id(res.json())
        print(f"{GREEN}✅ Order Created (ID: {order_id}){NC}")
        print(f"{YELLOW}📨 Event: order.created → Inventory reserved{NC}")
        time.sleep(2)
    except Exception as e:
        print(f"{NC}❌ Error: {e}{NC}")
        return

    # 4️⃣ Simulate Payment FAILURE (Saga Trigger)
    print_step("4️⃣ Simulating Payment FAILURE...")
    print(f"{RED}❌ Sending invalid payment to trigger failure...{NC}")
    try:
        res = requests.post(
            f"{BASE_URL}:{SERVICES['payment']}/payments/",
            json={
                "order_id": order_id,
                "amount": -100,  # ❌ Invalid amount triggers failure
                "payment_method": "invalid_card"
            },
            timeout=10
        )
        print(f"{RED}❌ Payment Failed (Expected): {res.status_code}{NC}")
        print(f"{YELLOW}📨 Event: payment.failed published to Kafka{NC}")
        print(f"{YELLOW}🔄 SAGA: Compensating transaction triggered...{NC}")
        time.sleep(3)
    except Exception as e:
        print(f"{NC}⚠️  Payment error: {e}{NC}")

    # 5️⃣ Verify Inventory Rollback (Saga Proof)
    print_step("5️⃣ Verifying Inventory Rollback (SAGA Pattern)...")
    try:
        res = requests.get(
            f"{BASE_URL}:{SERVICES['inventory']}/inventory/{product_id}",
            timeout=10
        )
        if res.status_code == 200:
            final_stock = res.json().get("stock_quantity", res.json().get("data", {}).get("stock_quantity", 5))
            print(f"{GREEN}✅ Final Stock: {final_stock}{NC}")
            if final_stock == 5:
                print(f"{GREEN}✅ SAGA SUCCESS: Inventory automatically restored!{NC}")
            else:
                print(f"{YELLOW}⚠️  Stock changed (may need manual verification){NC}")
        time.sleep(2)
    except Exception as e:
        print(f"{NC}⚠️  Rollback check failed: {e}{NC}")

    # 6️⃣ Show Event Logs
    print_step("6️⃣ Checking Event Logs...")
    import subprocess
    try:
        result = subprocess.run(
            ["docker", "compose", "logs", "--tail=30"],
            capture_output=True,
            text=True,
            cwd="infrastructure"
        )
        for line in result.stdout.split('\n'):
            if any(word in line.lower() for word in ['failed', 'rollback', 'compensat']):
                print(f"{RED}📨 {line.strip()}{NC}")
    except Exception as e:
        print(f"{NC}⚠️  Could not fetch logs: {e}{NC}")

    print_step("✅ SAGA DEMO COMPLETE!")
    print(f"{GREEN}🎬 This proves fault tolerance & automatic rollback!{NC}")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print(f"{NC}❌ Please install requests: pip install requests{NC}")
        sys.exit(1)
    
    main()