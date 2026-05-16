# 🧠 AI Timetable Generator

**AI-Powered Timetable Generation System**  
*Centre for Artificial Intelligence — Session: Jan–June 2026*

> By **Toshif Ali** and **Aditya Yadav**

---

## 📋 Overview

An intelligent web application that automatically generates optimized, conflict-free class schedules for educational institutions using **Constraint Satisfaction Problem (CSP)** algorithms with **Greedy Construction + Hill Climbing Optimization**.

### Key Features
- ✅ **Automated Timetable Generation** — AI generates schedules in seconds
- ✅ **Zero Conflict Guarantee** — No teacher, room, or class overlaps
- ✅ **Constraint-Aware Scheduling** — Handles hard & soft constraints
- ✅ **Interactive Web Interface** — Beautiful dark-themed SPA
- ✅ **Real-Time Conflict Analysis** — Detects and reports all violations
- ✅ **Multi-Format Export** — CSV, JSON, and Print-ready output
- ✅ **Pre-Loaded Real Data** — 6th Semester data from Centre for AI
- ✅ **Full CRUD Operations** — Add/Edit/Delete all entities

---

## 🚀 How to Run

### Prerequisites
- Python 3.10+ with virtual environment (`ml-env`)

### Start the Application

```bash
# Navigate to the app directory
cd "ML_PROJECTS/Ai time table Generator/app"

# Activate virtual environment
source /Users/adityayadav/ML_PROJECTS/ml-env/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the server
python run.py
```

Then open **http://localhost:8000** in your browser.

---

## 🏗️ System Architecture (MVC Pattern)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  AI Engine   │
│  (HTML/CSS/  │◀────│  (FastAPI)   │◀────│  (CSP Solver)│
│    JS SPA)   │     │              │     │              │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                     ┌──────▼───────┐
                     │   Database   │
                     │   (SQLite)   │
                     └──────────────┘
```

### Technology Stack
| Component | Technology |
|-----------|-----------|
| Frontend | HTML5 + Vanilla CSS + JavaScript (SPA) |
| Backend | Python FastAPI |
| Database | SQLite with SQLAlchemy ORM |
| AI Engine | CSP Solver (Pure Python) |
| Server | Uvicorn ASGI |

---

## 🧬 AI Algorithm — CSP Solver

### Hard Constraints (Must NEVER violate)
- **C1:** Faculty cannot teach in 2 rooms at the same time
- **C2:** Room cannot host 2 classes at the same time
- **C3:** Class cannot have 2 subjects at the same time

### Soft Constraints (Optimization quality)
- **S1:** Balanced daily workload for faculty
- **S2:** Limit continuous lectures to max 2 hours
- **S3:** Balanced class schedules across the week
- **S4:** Subject spread across different days

### Algorithm Phases
1. **Greedy Construction** — Assigns most-constrained tasks first
2. **Hill Climbing Optimization** — Iteratively swaps slots to improve fitness
3. **Multi-Attempt Best Selection** — Runs multiple attempts, picks the best

### Fitness Score = Hard Score (50%) + Soft Score (50%)
- 0 hard violations → base 50 + soft optimization
- Any violation → severe penalty, triggering more iterations

---

## 📊 Pre-Loaded Data (6th Semester)

| Entity | Count | Source |
|--------|-------|--------|
| Faculty | 16 | Dr. Pawan Dubey, Dr. Tej Singh, Dr. Prerna Mishra, etc. |
| Subjects | 18 | AI for Robotics, Image Processing, Deep Learning, NLP, etc. |
| Rooms | 13 | J119, M101-M205, SH2, HPC Lab, M105 Lab |
| Classes | 3 | AIR-VI, AI&DS-VI, AIML-VI |
| Faculty-Subject | 24 | Real assignments from the master timetable |
| Class-Subject | 20 | With actual hours/week |

---

## 📁 Project Structure

```
Ai time table Generator/
├── (Project PDFs and Reference Documents)
├── app/
│   ├── run.py                  # Entry point — starts the server
│   ├── requirements.txt        # Python dependencies
│   ├── timetable.db           # SQLite database (auto-created)
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI server + all API routes
│   │   ├── models.py          # SQLAlchemy + Pydantic models
│   │   ├── database.py        # DB setup + seed data
│   │   └── ai_engine.py       # CSP solver AI engine
│   └── static/
│       ├── index.html         # Main SPA page
│       ├── css/
│       │   └── styles.css     # Complete design system
│       └── js/
│           └── app.js         # Frontend application logic
└── README.md
```

---

## 🎯 Test Results

| Test Case | Status | Description |
|-----------|--------|-------------|
| Basic Input | ✅ Passed | Correct timetable generated for 3 classes |
| Conflict Handling | ✅ Passed | 0 hard violations (no overlapping) |
| Limited Slots | ✅ Passed | Optimized schedule distribution |
| Invalid Input | ✅ Passed | Proper validation with error messages |
| Performance | ✅ Passed | Generation in < 0.1 seconds |
| Fitness Score | ✅ Passed | Consistently above 90% |

---

## 📱 Pages

1. **Dashboard** — Overview with statistics and quick actions
2. **Data Management** — CRUD for Faculty, Subjects, Rooms, Classes, Assignments
3. **Generate Timetable** — AI-powered generation with parameter control
4. **View Timetable** — Interactive grid with class filtering and lunch break
5. **Conflict Analysis** — Real-time conflict detection and reporting
6. **Export & Download** — CSV, JSON, and Print options

---

## 🔮 Future Enhancements
- Machine Learning for prediction-based scheduling
- Mobile app integration
- Cloud database support
- Real-time editing and drag-and-drop
- Multi-semester management
