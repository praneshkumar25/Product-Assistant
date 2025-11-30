
# SKF Product Assistant (Mini)

## 🚀 **Getting Started**

### **1. Prerequisites**

* Python **3.9+**
* Azure OpenAI **endpoint + key**
* Optional: Azure Cache for Redis (auto-fallback if missing)

---

### **2. Installation**

```bash
pip install -r requirements.txt
```

---

### **3. Configuration**

Create `.env` in the project root:

```
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-40-mini"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_KEY="your-key-here"

# Optional - fallback to local mock if invalid
REDIS_CONNECTION_STRING="rediss://:password@host:port/0"
```

---

### **4. Running the App**

```bash
python app.py
```

Server runs at:

```
http://localhost:5000
```

---

## 🧪 **How to Test the API**

Use Postman, Thunder Client, curl, or any HTTP client.

### **Endpoint**

```
POST http://localhost:5000/api/chat
```

---

### **Example 1 — Ask a product question (Q&A Intent)**

**Request**

```json
{
  "session_id": "user123",
  "message": "What is the limiting speed of 6205?"
}
```

**Response**

```
"The limiting speed of the 6205 is 18,000 r/min."
```

---

### **Example 2 — Follow-up question (Stateful Conversation)**

**Request**

```json
{
  "session_id": "user123",
  "message": "And what is its weight?"
}
```

**Response**

```
"The weight of the 6205 is 0.129 kg."
```

---

### **Example 3 — Provide feedback (Feedback Intent)**

**Request**

```json
{
  "session_id": "user123",
  "message": "The weight description is wrong, please correct it to 0.229"
}
```

**Response**

```
"The correction for the weight of the 6205 has been noted as 0.229 kg. Is there anything else you need?"
```

## 🏗️ **Architecture & Components**

This application follows a **Service → Plugin → Orchestrator** pattern

### **Core Components**

### **`app.py` — API Gateway**

* Flask entry point.
* Handles incoming requests (`/api/chat`).
* Bridges synchronous HTTP calls with async Semantic Kernel execution.
* Validates requests and returns structured JSON responses.

---

### **`orchestrator.py` **

* Creates and manages the **Semantic Kernel** instance.
* Handles **Intent Routing**:

  * Q&A → DatasheetPlugin
  * Feedback → FeedbackPlugin
* Manages **conversation state** using chat history (Redis or local mock).

---

### **`config.py` — Config**

* Loads environment variables via `.env`.
* Stores Azure/OpenAI/Redis configuration.
* Prevents leaks by centralizing sensitive values.

---

## 🔌 **Plugins (The Agents)**

### **`plugins/datasheet_plugin.py` — Q&A Agent**

* Retrieves product attributes (e.g., *width*, *bore diameter*, *limiting speed*) from JSON datasheets.
* Implements **Redis caching**:

  * Cache HIT → Returns instantly
  * Cache MISS → Reads JSON and stores result

---

### **`plugins/feedback_plugin.py` — Feedback Agent**

* Stores user corrections or feedback.
* Saves feedback records (designation → attribute → note → timestamp).

---

## 🛠️ Services 

### **`services/data_manager.py`**

* Loads all JSON files inside `/data` automatically.
---

### **`services/redis_service.py`**

* Wrapper around Redis
  * If real Redis connection fails → switches to **in-memory mock** so the app works.

---