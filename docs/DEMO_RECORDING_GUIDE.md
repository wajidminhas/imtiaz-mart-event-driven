# 🎬 DEMO RECORDING - QUICK REFERENCE CARD

## 📋 **Recording Checklist**

### **Before Recording:**
- [ ] All services running: `docker compose ps`
- [ ] Open these tabs in browser:
  1. `docs/event-driven-architecture-demo.html`
  2. http://localhost:8080 (Kafka UI)
  3. http://localhost:8003/docs (Order Service)
  4. http://localhost:8004/docs (Inventory Service)
  5. http://localhost:8002/docs (Payment Service)
- [ ] Microphone tested
- [ ] Recording started (OBS/Loom)

---

## ⏱️ **2.5 Minute Script**

| Time | Show | Say |
|------|------|-----|
| **0:00-0:20** | Architecture HTML | "Production-grade event-driven platform. 5 services, Kafka, async communication." |
| **0:20-0:40** | Kafka UI (Topics) | "16 event topics. Every action publishes events. Event-driven engineering." |
| **0:40-1:15** | Order Swagger | "Creating order via Swagger... Event published to Kafka. Loose coupling." |
| **1:15-1:35** | Inventory Swagger | "Inventory auto-updated via events. No API calls. Event-driven workflow." |
| **1:35-2:00** | Payment Swagger | "Saga pattern: Order → Payment → Inventory. All through events." |
| **2:00-2:15** | Kafka UI (Messages) | "Event sourcing: All events persisted. Audit trail. Replay capability." |
| **2:15-2:30** | Architecture HTML | "10x scalability, zero downtime. Need this? Let's talk!" |

---

## 🎯 **Key Points to Hit**

### **Must Say:**
✅ "Event-driven architecture"
✅ "Apache Kafka - 16 topics"
✅ "Loose coupling"
✅ "Async communication"
✅ "Saga pattern"
✅ "Event sourcing"
✅ "5 independent microservices"

### **Must Show:**
✅ Architecture diagram
✅ Kafka topics list
✅ Creating order in Swagger
✅ Event appearing in Kafka UI
✅ Inventory auto-updated
✅ Payment flow
✅ Event message payload

---

## 🔗 **Quick Links**

```
Architecture:  docs/event-driven-architecture-demo.html
Kafka UI:      http://localhost:8080
Order API:     http://localhost:8003/docs
Inventory API: http://localhost:8004/docs
Payment API:   http://localhost:8002/docs
```

---

## 🎬 **Step-by-Step Flow**

### **1. Architecture (20 sec)**
- Show: `event-driven-architecture-demo.html`
- Point to: 5 services, 16 topics
- Say: "Event-driven microservices platform"

### **2. Kafka Topics (20 sec)**
- Switch to: Kafka UI (localhost:8080)
- Click: "Topics"
- Say: "16 event topics for async communication"

### **3. Create Order (35 sec)**
- Switch to: Order Service Swagger
- Expand: POST /v1/orders/
- Click: "Try it out"
- Enter: user_id: 1, items: [{product_id: 3, quantity: 2}]
- Click: "Execute"
- Say: "Order created → event published to Kafka"

### **4. Show Event (15 sec)**
- Switch to: Kafka UI
- Click: "Topics" → "order.created"
- Say: "Event published! Inventory Service will consume it"

### **5. Check Inventory (20 sec)**
- Switch to: Inventory Service Swagger
- Expand: GET /inventory/{product_id}
- Click: "Try it out", enter: 3
- Click: "Execute"
- Say: "Stock reserved automatically via events"

### **6. Payment Flow (30 sec)**
- Switch to: Payment Service Swagger
- Expand: POST /v1/payments/
- Click: "Try it out"
- Enter: order_id: 2, amount: 500000, payment_method: stripe
- Click: "Execute"
- Expand: POST /v1/payments/{id}/complete
- Complete payment
- Say: "Saga pattern: Order → Payment → Inventory"

### **7. Event Sourcing (15 sec)**
- Switch to: Kafka UI
- Click: "payment.completed" topic
- View messages
- Say: "All events persisted. Audit trail. Replay capability."

### **8. Close (15 sec)**
- Switch to: Architecture HTML
- Show: Business value section
- Say: "10x scalability, zero downtime. Contact me!"

---

## 💡 **Pro Tips**

### **While Recording:**
- Speak clearly and slowly
- Pause between sections
- Point with mouse cursor
- Don't rush - 2.5 minutes is enough
- Smile when showing contact info

### **If You Make a Mistake:**
- Pause for 3 seconds
- Continue from that point
- Edit out the pause later
- Don't restart the whole video

### **Mouse Movement:**
- Move slowly and deliberately
- Hover over important elements
- Click with purpose
- Don't shake the cursor

---

## 🎯 **Demo Data to Use**

### **For Order Creation:**
```json
{
  "user_id": 1,
  "items": [
    {
      "product_id": 3,
      "quantity": 2,
      "price": 250000
    }
  ],
  "shipping_address": "123 Main St, Karachi"
}
```

### **For Payment:**
```json
{
  "order_id": 2,
  "user_id": 1,
  "amount": 500000,
  "payment_method": "stripe",
  "payment_provider": "stripe"
}
```

### **For Completion:**
```
payment_id: [use ID from payment response]
provider_transaction_id: txn_12345
```

---

## ✅ **Post-Recording**

- [ ] Stop recording
- [ ] Save/upload video
- [ ] Watch it once (quality check)
- [ ] Upload to:
  - Loom (shareable link)
  - YouTube (unlisted)
  - Vimeo
- [ ] Add to:
  - Fiverr gig description
  - Upwork portfolio
  - Proposal responses

---

## 🆘 **Troubleshooting**

### **If Swagger UI not loading:**
```bash
curl http://localhost:8003/health
# If not responding, restart:
cd infrastructure
docker compose restart order-service
```

### **If Kafka UI not showing events:**
- Create a test order first
- Wait 5-10 seconds for event to appear
- Refresh the page

### **If services not running:**
```bash
cd infrastructure
docker compose up -d
sleep 30
docker compose ps
```

---

## 📞 **Contact Info to Show**

```
Email: shanitent667@gmail.com
GitHub: https://github.com/wajidminhas
Fiverr: [Your Fiverr Profile URL]
Upwork: [Your Upwork Profile URL]
```

---

<div align="center">

**🎯 You're Ready! Hit Record and Crush It!**

**Remember: Show the events, explain the value, close strong!**

**🚀**

</div>
