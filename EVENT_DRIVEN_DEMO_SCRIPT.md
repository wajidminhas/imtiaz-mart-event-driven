# 🎬 Event-Driven Architecture Demo - Swagger UI Version

## 🎯 **Demo Focus: Show EVENT-DRIVEN ENGINEERING Excellence**

**Platform:** Swagger UI (No CLI/Terminal)
**Duration:** 2-3 Minutes

---

## 📹 **2-Minute Demo Script (Swagger UI Only)**

### **0:00-0:20 → Hook: Architecture Overview**

**Show:** `docs/event-driven-architecture-demo.html`

**Say:**
> "This is a **production-grade event-driven microservices platform** I built.
> 
> **5 distributed services** communicating **asynchronously** via **Apache Kafka**.
> 
> No tight coupling. No synchronous calls. Pure event-driven architecture."

**Action:** Point to the 16 event topics shown on the page.

---

### **0:20-0:40 → Show Kafka Event Bus**

**Show:** Kafka UI (http://localhost:8080) → Click "Topics"

**Say:**
> "Here are **16 event topics** powering this system:
> - `user.registered`, `user.updated`
> - `product.created`, `product.updated`
> - `order.created`, `order.confirmed`, `order.cancelled`
> - `payment.initiated`, `payment.completed`, `payment.failed`
> - `inventory.updated`, `inventory.low-stock`
> 
> **Every action publishes events. Every service reacts to events.**
> This is **event-driven engineering** at scale."

---

### **0:40-1:15 → Live Event Demo: Order → Inventory (Swagger UI)**

**Show:** Split screen - Order Service Swagger + Inventory Service Swagger

**Step 1 - Open Order Service Swagger:**
- Navigate to: http://localhost:8003/docs
- Expand: `POST /v1/orders/`

**Say:**
> "Watch this event-driven workflow. I'm in the Order Service Swagger UI.
> When I create an order, it won't call Inventory directly..."

**Step 2 - Click "Try it out" and enter:**
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

**Step 3 - Click "Execute"**

**Say:**
> "Order created! Now watch the magic..."

**Step 4 - Switch to Kafka UI (http://localhost:8080)**
- Click on "Topics"
- Find `order.created` topic
- Click to view messages

**Say:**
> "See that? **`order.created` event published to Kafka**.
> The Order Service doesn't call Inventory Service directly.
> It just publishes an event. **Loose coupling.**"

**Step 5 - Switch to Inventory Service Swagger:**
- Navigate to: http://localhost:8004/docs
- Expand: `GET /inventory/{product_id}`
- Click "Try it out", enter product_id: 3
- Click "Execute"

**Say:**
> "The Inventory Service **consumed the event asynchronously** and 
> **automatically reserved stock**. No synchronous API calls.
> **Event-driven workflow complete.**"

**Point out:** The quantity decreased by 2 (from 50 to 48).

---

### **1:15-1:45 → Show Saga Pattern (Payment Flow)**

**Show:** Payment Service Swagger UI

**Step 1 - Open Payment Service Swagger:**
- Navigate to: http://localhost:8002/docs
- Expand: `POST /v1/payments/`

**Say:**
> "Here's where it gets advanced. Watch the **Saga pattern** in action."

**Step 2 - Click "Try it out" and enter:**
```json
{
  "order_id": 2,
  "user_id": 1,
  "amount": 500000,
  "payment_method": "stripe",
  "payment_provider": "stripe"
}
```

**Step 3 - Click "Execute"**

**Say:**
> "Payment initiated. Now I'll complete it..."

**Step 4 - Expand: `POST /v1/payments/{payment_id}/complete`**
- Click "Try it out"
- Enter payment_id: (use the ID from previous response)
- Enter provider_transaction_id: `txn_12345`
- Click "Execute"

**Say:**
> "Payment completed → publishes `payment.completed` event →
> Order Service consumes it → updates order status to CONFIRMED.
> 
> **This is a distributed saga across 3 services:**
> Order → Payment → Inventory
> 
> **All coordinated through events. No two-phase commit.**"

**Step 5 - Show Order Status:**
- Navigate to: http://localhost:8003/docs
- Expand: `GET /v1/orders/{order_id}`
- Execute to show order status is now "CONFIRMED"

---

### **1:45-2:00 → Show Event Sourcing Benefits**

**Show:** Kafka UI → Click on `payment.completed` topic → View messages

**Say:**
> "Every event is **persisted in Kafka**. This gives us:
> - **Audit trail** - Complete history of every change
> - **Event replay** - Can rebuild state from events
> - **Debugging** - See exactly what happened when
> - **CQRS ready** - Separate read/write models
> 
> This is **event sourcing** in production."

**Click on a message to show the payload.**

---

### **2:00-2:15 → Show All Services Health**

**Show:** Quick tour of all Swagger UIs

**Say:**
> "All services are running and healthy:
> - User Service: http://localhost:8000/docs
> - Product Service: http://localhost:8001/docs
> - Payment Service: http://localhost:8002/docs
> - Order Service: http://localhost:8003/docs
> - Inventory Service: http://localhost:8004/docs
> 
> Built with **Dapr service mesh** for production reliability."

---

### **2:15-2:30 → Close with Business Value**

**Show:** `docs/event-driven-architecture-demo.html` (Business Value section)

**Say:**
> "This architecture gives you:
> - **10x scalability** - Scale services independently
> - **Zero downtime** - Deploy services separately
> - **Fault isolation** - One service fails, others continue
> - **Real-time updates** - Events flow instantly
> 
> Need this level of engineering for your business?
> Let's talk."

**Show your contact info.**

---

## 🎯 **Browser Tabs to Keep Open**

| Tab | URL | Purpose |
|-----|-----|---------|
| 1 | `docs/event-driven-architecture-demo.html` | Architecture overview |
| 2 | http://localhost:8080 | Kafka UI (events) |
| 3 | http://localhost:8003/docs | Order Service (create order) |
| 4 | http://localhost:8004/docs | Inventory Service (check stock) |
| 5 | http://localhost:8002/docs | Payment Service (process payment) |

---

## 🎬 **Step-by-Step Navigation Guide**

### **Before Recording:**
1. ✅ Start all services: `docker compose up -d`
2. ✅ Open all 5 tabs listed above
3. ✅ Create a test product (so you have product_id to use)
4. ✅ Test all Swagger UIs are working
5. ✅ Microphone check

### **Recording Flow:**
```
1. Tab 1: Architecture diagram (20 sec)
2. Tab 2: Kafka topics (20 sec)
3. Tab 3: Create order via Swagger (35 sec)
4. Tab 2: Show order.created event (15 sec)
5. Tab 4: Check inventory updated (20 sec)
6. Tab 5: Create & complete payment (30 sec)
7. Tab 2: Show payment.completed event (15 sec)
8. Tab 1: Business value close (15 sec)
```

**Total: ~2.5 minutes**

---

## 💡 **Pro Tips for Swagger UI Demo**

### **1. Highlight the "Try it out" Button**
```
"This interactive API documentation lets you test every endpoint.
Clients love this - no Postman needed!"
```

### **2. Show Response Times**
```
Point to the response time shown in Swagger:
"Look at that - 45ms response time. FastAPI + async processing."
```

### **3. Show Request/Response Payloads**
```
"See this JSON structure? Clean, typed, validated.
Pydantic models ensure data integrity."
```

### **4. Show Multiple Endpoints**
```
Don't just show POST - also show GET, PUT endpoints
"Full CRUD operations, all documented automatically."
```

### **5. Show the "Authorize" Button**
```
"JWT authentication built-in. Click Authorize,
enter your token, and all endpoints are secured."
```

---

## 🎯 **Key Engineering Concepts to Highlight**

### **1. Event-Driven Architecture (EDA)**
```
❌ Don't say: "I created an order"
✅ Say: "Order Service published an event that triggered 
        downstream workflows in Inventory and Payment"
```

### **2. Loose Coupling**
```
❌ Don't say: "Services talk to each other"
✅ Say: "Services are decoupled - they only know about events, 
        not about each other"
```

### **3. Async Communication**
```
❌ Don't say: "It updates inventory"
✅ Say: "Inventory Service asynchronously consumes order events 
        and updates stock levels"
```

### **4. Saga Pattern**
```
❌ Don't say: "Payment works"
✅ Say: "Distributed saga coordinates Order → Payment → Inventory 
        through choreographed events"
```

### **5. Event Sourcing**
```
❌ Don't say: "Database stores data"
✅ Say: "Kafka persists all events, giving us audit trail, 
        replay capability, and CQRS foundation"
```

---

## 📊 **Business Value Talking Points**

### **When Client Asks "Why Event-Driven?"**
```
✅ "Event-driven means:
- Add new features without changing existing code
- Just consume events (notifications, analytics, reporting)
- Zero downtime deployments
- Fault isolation - one service fails, others continue

This is how Netflix, Amazon, Uber build systems."
```

### **When Client Asks "Why Kafka?"**
```
✅ "Kafka gives us:
- Durable event storage (events persist for replay)
- High throughput (millions of events per second)
- Multiple consumers (many services react to same event)
- Event streaming (real-time processing)

This is enterprise-grade messaging, not just a queue."
```

### **When Client Asks "What About Data Consistency?"**
```
✅ "We use the Saga pattern:
- Each service has its own database
- Distributed transactions via events
- If payment fails → publish 'payment.failed'
- Order cancels, inventory restores

This is **eventual consistency** - system converges to correct state."
```

---

## 📸 **Screenshots to Capture from Swagger**

1. **Order Service Swagger** - POST /orders/ endpoint
2. **Inventory Service Swagger** - GET /inventory/{id} showing updated stock
3. **Payment Service Swagger** - POST /payments/ and complete endpoint
4. **Kafka UI** - Topics list with all 16 topics
5. **Kafka UI** - Message details (event payload)
6. **Architecture Diagram** - From the HTML page

---

## 🚀 **Recording Tools**

### **Best Options:**

**1. OBS Studio (Free, Professional)**
- Download: obsproject.com
- Settings: 1920x1080, 30fps
- Record browser tabs
- Record locally, upload to YouTube/Vimeo

**2. Loom (Easiest)**
- loom.com
- Chrome extension
- Auto-uploads, shareable link
- Free plan: 25 videos, 5 min each

**3. Screenity (Chrome Extension)**
- Free, unlimited
- Records screen + webcam
- No time limits

---

## ✅ **Pre-Recording Checklist**

- [ ] All services running (`docker compose ps`)
- [ ] All 5 browser tabs open (listed above)
- [ ] Kafka UI has some existing events
- [ ] Test product exists (product_id: 3)
- [ ] Swagger UIs working (test one endpoint)
- [ ] Microphone tested
- [ ] Recording software configured
- [ ] Script printed/visible

---

## 🎬 **Final Script (Condensed)**

```
[0:00] "Hi, I'm Wajid. Let me show you a production-grade 
        event-driven microservices platform."
        → Show architecture diagram

[0:20] "Five services. Apache Kafka with 16 event topics.
        Async communication. No tight coupling."
        → Show Kafka UI

[0:40] "Watch this: I create an order via Swagger UI..."
        → Order Service Swagger, click Execute
        "Event published to Kafka."

[0:55] "Inventory Service consumes it automatically.
        No API calls. Pure event-driven."
        → Show Inventory updated in Swagger

[1:15] "Payment completes via Swagger, publishes event.
        Order Service consumes, confirms order.
        This is the Saga pattern."
        → Payment Service Swagger

[1:45] "Every event persisted in Kafka.
        Audit trail. Event replay. CQRS ready."
        → Show Kafka message details

[2:00] "This architecture scales to millions of events.
        Used by Amazon, Netflix, Uber.
        
        Need this for your business? Let's talk."
        → Show contact info

[2:30] [End]
```

---

## 🔗 **Quick Links for Demo**

```
Architecture Diagram:  file:///.../docs/event-driven-architecture-demo.html
Kafka UI:              http://localhost:8080
User Service Swagger:  http://localhost:8000/docs
Product Service:       http://localhost:8001/docs
Payment Service:       http://localhost:8002/docs
Order Service:         http://localhost:8003/docs
Inventory Service:     http://localhost:8004/docs
```

---

<div align="center">

**🎯 Record This. Share It. Win Clients.**

**Your event-driven expertise is your competitive advantage.**

**Show it proudly!** 🚀

</div>
