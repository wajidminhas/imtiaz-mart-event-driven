#!/bin/bash
echo "🎬 Starting Imtiaz Mart Demo Flow..."

echo "1️⃣ Registering User..."
curl -s -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"pass123","name":"Demo User"}'

echo "2️⃣ Creating Product..."
curl -s -X POST http://localhost:8001/products/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","price":1000,"stock_quantity":5}' 

echo "3️⃣ Placing Order..."
curl -s -X POST http://localhost:8003/orders/ \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"items":[{"product_id":1,"quantity":1,"price":1000}]}' 

echo "4️⃣ Processing Payment..."
curl -s -X POST http://localhost:8002/payments/ \
  -H "Content-Type: application/json" \
  -d '{"order_id":1,"amount":1000,"payment_method":"card"}' 

echo "✅ Demo Complete!"
