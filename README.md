# FastAPI JWT Authentication Backend

A production-ready FastAPI backend with JWT authentication, user registration/login, SQLAlchemy ORM, and SQLite database.

## Features

- **FastAPI** - Modern Python web framework
- **JWT Authentication** - Token-based authentication with cookies
- **Bcrypt Password Hashing** - Secure password storage
- **SQLAlchemy** - ORM for database management
- **SQLite Database** - Lightweight SQL database
- **Pydantic** - Data validation and settings management
- **CORS Support** - Cross-origin request handling
- **Admin-only Login** - Restricted login for admin roles

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and environment variables
│   ├── database.py          # Database setup and session management
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # User database model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py          # Pydantic schemas for validation
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py          # Authentication endpoints
│   ├── utils/
│   │   ├── __init__.py
│   │   └── auth.py          # JWT and password utilities
│   └── middleware/
│       ├── __init__.py
│       └── auth.py          # Authentication middleware
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── test.db                  # SQLite database (auto-created)
```

## Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
NOTE: run command in postgresql "CREATE EXTENSION postgis;"


### 3. Configure Environment Variables
Edit `.env` file:
```env
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Run the Server
```bash
python -m uvicorn app.main:app --reload
```

Server runs at: `http://127.0.0.1:8000`
API Docs: `http://127.0.0.1:8000/docs`

## API Endpoints
