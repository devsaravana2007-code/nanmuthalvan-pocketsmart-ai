# 💼 PocketSmart AI

**AI-Powered Budget Planning for Everyday Needs**

A GenAI-powered budget & recommendation assistant built with **FastAPI + Gemini 3.6 Flash  + Jinja2**.

## ✨ Features

- 🏠 **Home Interior Planner** — budget breakdown for lights, fans, furniture, dining
- 🎉 **Party Planner** — venue, catering, decoration & entertainment allocation
- 💎 **Jewelry Planner** — text + image multimodal matching for occasions
- 🔐 **JWT Auth** — Register, Login, Logout, session management
- 🕘 **History** — replay past recommendations
- 🛒 **Real shopping links** — Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO, Bluestone, Tanishq
- 🧠 **Offline mode** — works without a Gemini key using smart fallback logic

## 🚀 Quick Start

    pip install -r requirements.txt
    cp .env.example .env
    python app.py

Open **http://127.0.0.1:8000**

**Demo login:** sai / test1234

## 🏗️ Tech Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI, Uvicorn |
| AI | Google Gemini 1.5 Flash Pro |
| Frontend | Jinja2, HTML5, CSS3, Vanilla JS |
| Auth | JWT (PyJWT), PBKDF2-SHA256 |
| Images | Pillow (multimodal) |

## 📁 Project Structure

    PocketSmart/
    ├── app.py                # FastAPI routes
    ├── gemini_utils.py       # AI logic + offline fallback
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    ├── templates/            # Jinja2 pages
    │   ├── base.html
    │   ├── index.html
    │   ├── login.html
    │   ├── register.html
    │   ├── dashboard.html
    │   ├── home_planner.html
    │   ├── party_planner.html
    │   ├── jewelry_planner.html
    │   └── history.html
    └── static/
        ├── styles.css
        └── uploads/

## 🔐 Environment Variables

Copy `.env.example` to `.env` and fill in:

    SECRET_KEY=your-random-long-secret
    GOOGLE_API_KEY=your-gemini-key-here

> **Note:** `GOOGLE_API_KEY` is optional. Without it, the app runs in offline demo mode with realistic fallback recommendations.

## 🧪 Usage

1. Visit **http://127.0.0.1:8000**
2. Click **Get Started** → Register OR use demo: `sai` / `test1234`
3. Choose a planner: 🏠 Home · 🎉 Party · 💎 Jewelry
4. Enter your budget → get instant recommendations
5. Check **History** to review past plans

## 📄 License

MIT — free to use, learn, and modify.
y.
