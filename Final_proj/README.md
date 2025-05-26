
# Flipr Support AI

**Flipr Support AI** is a multi-tenant AI-powered customer support system that enables companies to manage customer queries using an intelligent chatbot, route unresolved issues to human agents, and track support performance via dashboards.

---

## 📁 Folder Structure

```
FLIPRSUPPORTAI/
├── .venv/                     # Virtual environment (ignored in Git)
├── app/
│   ├── routes/                # API endpoints
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── chatbot.py
│   │   ├── dashboard.py
│   │   ├── feedback.py
│   │   └── tickets.py
│   └── services/              # Core AI & business logic
│       ├── ai_assist.py
│       ├── ai_chat.py
│       ├── embedding_model.py
│       ├── metrics.py
│       └── ticket_automation.py
├── utils/                     # Utilities
│   ├── database.py
│   ├── security.py
│   └── models.py              # SQLAlchemy models
├── instance/
│   └── app.db                 # SQLite DB
├── static/                    # Static assets
├── templates/                 # HTML templates
├── .env                       # Environment variables
├── config.py                  # Config settings
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
└── run.py                     # App entry point
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/flipr-support-ai.git
cd flipr-support-ai
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file in the root directory:

```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### 5. Run the Application

```bash
python run.py
```

> Access it locally at `http://127.0.0.1:5000`

---

## 📡 API Overview (Examples)

### 🔐 Auth

- **POST /register**
- **POST /login**

### 💬 Chatbot

- **POST /chat**  
  `{"company_id": 1, "user_id": 2, "question": "What is your refund policy?"}`

### 🎫 Tickets

- **POST /tickets**  
- **GET /tickets**

---

## 📊 Dashboards

Available for:
- Admins: Company-level analytics
- Agents: Assigned tickets & performance
- Customers: Ticket status & chat logs

---

## 🧠 AI Features

- FAQ & Article-based QA using Transformers (`distilbert-base-cased-distilled-squad`)
- Ticket auto-triage with embeddings
- Low-confidence fallback → ticket creation
- Agent assistant (WIP)

---

## 🏗 Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **AI/ML**: Hugging Face Transformers, SentenceTransformers
- **DB**: SQLite (dev)

---
