# Product Persistence & Price Monitoring System

A full-stack application for automated, persistent product price and stock monitoring across multiple online stores. Built with **FastAPI**, **PostgreSQL**, **APScheduler**, and **Next.js**.

---

## 🏗️ Architecture & Features

- **Backend (FastAPI)**:
  - Automated recurring monitoring via **APScheduler**.
  - Product price tracking & stock state persistence.
  - Multi-store provider integration (Amazon, Walmart, eBay, Target, BestBuy).
  - Multi-channel alerts (Email via SMTP, SMS via Twilio).
  - JWT Authentication (Register, Login, Token Refresh).
  - Auto-generated Swagger interactive API documentation.
- **Frontend (Next.js 16 / React 19)**:
  - Modern dashboard built with Tailwind CSS & Lucide icons.
  - Dynamic charts visualizing price history trends (**Recharts**).
  - Product request management & real-time notification feeds.

---

## 🛠️ Prerequisites

Ensure you have the following installed on your machine:

1. **Python** (v3.10 or higher)
2. **Node.js** (v18.x or higher) and `npm`
3. **PostgreSQL Database** running locally or remotely

---

## 🚀 How to Run the Project

### 1. Database Setup

Ensure PostgreSQL service is running and create a database named `product_monitoring` (or update your connection URL accordingly):

```sql
CREATE DATABASE product_monitoring;
```

---

### 2. Backend Setup & Execution

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create & activate a virtual environment** (optional but recommended):
   - **Windows**:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   Create or edit the `.env` file inside `backend/` directory:
   ```env
   DATABASE_URL=postgresql://postgres:123456@localhost:5432/product_monitoring
   SECRET_KEY=your-super-secret-jwt-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440

   # Optional Email & SMS Settings
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   FROM_EMAIL=noreply@productmonitor.com

   TWILIO_ACCOUNT_SID=
   TWILIO_AUTH_TOKEN=
   TWILIO_PHONE_NUMBER=
   ```

5. **Start the Backend Server**:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   *The FastAPI server will automatically create all required database tables on startup.*

   - **API Documentation**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.
   - **Health Check**: Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

6. **Verify Backend Functionality (Optional)**:
   Run the test verification script to verify DB tables and scheduler execution:
   ```bash
   python verify_backend.py
   ```

---

### 3. Frontend Setup & Execution

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node dependencies**:
   ```bash
   npm install
   ```

3. **Environment Configuration**:
   Create or edit `.env.local` inside `frontend/`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start Development Server**:
   ```bash
   npm run dev
   ```

5. **Access the App**:
   Open [http://localhost:3000](http://localhost:3000) in your web browser.

---

## 📁 Directory Overview

```
product persistence/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entry point & routers
│   │   ├── config.py          # Environment settings
│   │   ├── database.py        # SQLAlchemy session & engine
│   │   ├── models/            # Database ORM models
│   │   ├── providers/         # E-commerce store provider scrapers
│   │   ├── routers/           # API Endpoints (auth, products, monitoring, notifications)
│   │   ├── scheduler/         # Background periodic monitoring jobs
│   │   ├── schemas/           # Pydantic data validation schemas
│   │   └── services/          # Business logic & alerts
│   ├── requirements.txt       # Python dependencies
│   ├── verify_backend.py      # Backend verification & simulation script
│   └── cleanup_db.py          # Database reset/clean helper script
└── frontend/
    ├── app/                   # Next.js App Router pages
    ├── components/            # UI components & charts
    ├── lib/                   # API client utilities
    └── package.json           # Frontend dependencies & scripts
```

---

## 🧪 Testing & Utilities

- **Reset Database**: To clear test data, execute:
  ```bash
  python backend/cleanup_db.py
  ```
- **Backend Verification**: To simulate price changes and notification triggers:
  ```bash
  python backend/verify_backend.py
  ```


### backend commands

cd "c:\Users\User\Documents\product persistence\backend"

# (Optional) Activate virtual environment if available:
# .\.venv\Scripts\activate

# Install dependencies if not already done:
pip install -r requirements.txt

# Start FastAPI dev server:
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000






### frontend commands

cd "c:\Users\User\Documents\product persistence\frontend"

# Install frontend dependencies:
npm install

# Start Next.js dev server:
npm run dev
