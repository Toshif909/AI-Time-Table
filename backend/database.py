"""
AI Timetable Generator — Database Setup & Seed Data
SQLite database initialization with real 6th Semester data from
Centre for Artificial Intelligence (Session: Jan-June 2026).
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from .models import (
    Base, Faculty, Subject, Room, ClassSection,
    FacultySubject, ClassSubject
)

# Database file path (alongside run.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "timetable.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency: yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def is_db_empty(db: Session) -> bool:
    """Check if the database needs seeding."""
    return db.query(Faculty).count() == 0


def seed_database():
    """
    Pre-populate the database with real data from the
    6th Semester Timetable — Centre for Artificial Intelligence.
    """
    db = SessionLocal()

    if not is_db_empty(db):
        db.close()
        return

    print("  📦 Seeding database with 6th Semester data...")

    # ──────────────────────────────────────────────
    #  FACULTY (from 6th_Sem_Updated_TT.pdf)
    # ──────────────────────────────────────────────
    faculty_data = [
        Faculty(name="Dr. Pawan Dubey", code="PD", department="Centre for AI", designation="Associate Professor", max_hours_per_day=6),
        Faculty(name="Dr. Tej Singh", code="TS", department="Centre for AI", designation="Associate Professor", max_hours_per_day=6),
        Faculty(name="Dr. Prerna Mishra", code="PM", department="Centre for AI", designation="Assistant Professor", max_hours_per_day=6),
        Faculty(name="Dr. Rahul Kumar Sharma", code="RKS", department="Centre for AI", designation="Assistant Professor", max_hours_per_day=5),
        Faculty(name="Ms. Reetu Shrivastava", code="RES", department="Centre for AI", designation="Assistant Professor", max_hours_per_day=5),
        Faculty(name="Dr. Rajni Ranjan Singh", code="RRS", department="Centre for AI", designation="Professor & Head", max_hours_per_day=4),
        Faculty(name="Dr. Abhishek Bhatt", code="AB", department="Centre for AI", designation="Associate Professor", max_hours_per_day=6),
        Faculty(name="Dr. Hardev Singh Pal", code="HSP", department="Centre for AI", designation="Associate Professor", max_hours_per_day=6),
        Faculty(name="Dr. Neelam Sharma", code="NS", department="Centre for AI", designation="Assistant Professor", max_hours_per_day=5),
        Faculty(name="Dr. Sunil Kumar Shukla", code="SKS", department="Centre for AI", designation="Assistant Professor", max_hours_per_day=5),
        Faculty(name="Ms. Pooja Tripathi", code="PT", department="Centre for AI", designation="Assistant Professor", max_hours_per_day=5),
        Faculty(name="Dr. Mausam Chouksey", code="MC", department="Centre for AI", designation="Assistant Professor", max_hours_per_day=5),
        Faculty(name="Dr. Nandkishor Joshi", code="NJ", department="Centre for AI", designation="Assistant Professor", max_hours_per_day=5),
        Faculty(name="Dr. Satyam Omar", code="SO", department="Centre for AI", designation="Assistant Professor", max_hours_per_day=5),
        Faculty(name="Dr. Neelam Arya", code="NA", department="Centre for AI", designation="Assistant Professor", max_hours_per_day=5),
        Faculty(name="Dr. Shubha Mishra", code="SM", department="Centre for AI", designation="Associate Professor", max_hours_per_day=5),
    ]
    db.add_all(faculty_data)
    db.flush()

    # Map faculty codes to IDs for quick lookup
    faculty_map = {f.code: f.id for f in faculty_data}

    # ──────────────────────────────────────────────
    #  SUBJECTS (from course code table)
    # ──────────────────────────────────────────────
    subjects_data = [
        # AIR Branch Subjects
        Subject(name="AI for Robotics", code="3240621", subject_type="theory", hours_per_week=3, color="#667eea"),
        Subject(name="Image Processing", code="3240622", subject_type="theory", hours_per_week=3, color="#06b6d4"),
        Subject(name="AI & Machine Learning", code="3240623", subject_type="theory", hours_per_week=4, color="#8b5cf6"),
        Subject(name="Minor Project-II (AIR)", code="3240624", subject_type="project", hours_per_week=2, color="#f59e0b"),
        Subject(name="AI & ML Lab", code="3240623L", subject_type="lab", hours_per_week=2, color="#ec4899"),

        # AI&DS Branch Subjects
        Subject(name="Natural Language Processing", code="3270621", subject_type="theory", hours_per_week=3, color="#10b981"),
        Subject(name="Image Processing (DS)", code="3270622", subject_type="theory", hours_per_week=3, color="#06b6d4"),
        Subject(name="Deep Learning", code="3270623", subject_type="theory", hours_per_week=4, color="#8b5cf6"),
        Subject(name="Minor Project-II (DS)", code="3270624", subject_type="project", hours_per_week=2, color="#f59e0b"),
        Subject(name="Deep Learning Lab (DS)", code="3270623L", subject_type="lab", hours_per_week=2, color="#ec4899"),
        Subject(name="Image Processing Lab (DS)", code="3270622L", subject_type="lab", hours_per_week=2, color="#22d3ee"),

        # AIML Branch Subjects
        Subject(name="NLP (AIML)", code="3280621", subject_type="theory", hours_per_week=3, color="#10b981"),
        Subject(name="Image Processing (ML)", code="3280622", subject_type="theory", hours_per_week=3, color="#06b6d4"),
        Subject(name="Deep Learning (ML)", code="3280623", subject_type="theory", hours_per_week=4, color="#8b5cf6"),
        Subject(name="Minor Project-II (ML)", code="3280624", subject_type="project", hours_per_week=2, color="#f59e0b"),
        Subject(name="Deep Learning Lab (ML)", code="3280623L", subject_type="lab", hours_per_week=2, color="#ec4899"),
        Subject(name="Image Processing Lab (ML)", code="3280622L", subject_type="lab", hours_per_week=2, color="#22d3ee"),

        # Common Subjects
        Subject(name="Intellectual Property Rights", code="1000007", subject_type="theory", hours_per_week=1, color="#6b7280"),
    ]
    db.add_all(subjects_data)
    db.flush()

    subject_map = {s.code: s.id for s in subjects_data}

    # ──────────────────────────────────────────────
    #  ROOMS (from timetable header)
    # ──────────────────────────────────────────────
    rooms_data = [
        Room(name="J119", capacity=80, is_lab=False, building="Main Block - First Floor"),
        Room(name="M101", capacity=60, is_lab=False, building="New Academic Block - First Floor"),
        Room(name="M102", capacity=60, is_lab=False, building="New Academic Block - First Floor"),
        Room(name="M103", capacity=60, is_lab=False, building="New Academic Block - First Floor"),
        Room(name="M104", capacity=60, is_lab=False, building="New Academic Block - First Floor"),
        Room(name="M105", capacity=40, is_lab=True, building="New Academic Block - First Floor"),
        Room(name="M201", capacity=60, is_lab=False, building="New Academic Block - Second Floor"),
        Room(name="M202", capacity=60, is_lab=False, building="New Academic Block - Second Floor"),
        Room(name="M203", capacity=60, is_lab=False, building="New Academic Block - Second Floor"),
        Room(name="M204", capacity=60, is_lab=False, building="New Academic Block - Second Floor"),
        Room(name="M205", capacity=60, is_lab=False, building="New Academic Block - Second Floor"),
        Room(name="SH2", capacity=120, is_lab=False, building="Main Block - Seminar Hall 2"),
        Room(name="HPC Lab", capacity=40, is_lab=True, building="Main Block - Ground Floor"),
    ]
    db.add_all(rooms_data)
    db.flush()

    # ──────────────────────────────────────────────
    #  CLASSES / SECTIONS
    # ──────────────────────────────────────────────
    classes_data = [
        ClassSection(name="AIR-VI", branch="AI & Robotics", semester=6, student_count=65),
        ClassSection(name="AI&DS-VI", branch="AI & Data Science", semester=6, student_count=65),
        ClassSection(name="AIML-VI", branch="AI & Machine Learning", semester=6, student_count=65),
    ]
    db.add_all(classes_data)
    db.flush()

    class_map = {c.name: c.id for c in classes_data}

    # ──────────────────────────────────────────────
    #  FACULTY ↔ SUBJECT ASSIGNMENTS
    # ──────────────────────────────────────────────
    faculty_subject_data = [
        # AIR subjects
        FacultySubject(faculty_id=faculty_map["PD"], subject_id=subject_map["3240621"]),   # PD teaches AI for Robotics
        FacultySubject(faculty_id=faculty_map["TS"], subject_id=subject_map["3240622"]),   # TS teaches Image Processing
        FacultySubject(faculty_id=faculty_map["PM"], subject_id=subject_map["3240623"]),   # PM teaches AI & ML
        FacultySubject(faculty_id=faculty_map["RRS"], subject_id=subject_map["3240624"]),  # RRS supervises Minor Project
        FacultySubject(faculty_id=faculty_map["PM"], subject_id=subject_map["3240623L"]),  # PM + Lab
        FacultySubject(faculty_id=faculty_map["RKS"], subject_id=subject_map["3240623L"]), # RKS assists Lab

        # AI&DS subjects
        FacultySubject(faculty_id=faculty_map["AB"], subject_id=subject_map["3270621"]),   # AB teaches NLP
        FacultySubject(faculty_id=faculty_map["TS"], subject_id=subject_map["3270622"]),   # TS teaches Image Processing
        FacultySubject(faculty_id=faculty_map["PM"], subject_id=subject_map["3270623"]),   # PM teaches Deep Learning
        FacultySubject(faculty_id=faculty_map["TS"], subject_id=subject_map["3270624"]),   # TS supervises Minor Project
        FacultySubject(faculty_id=faculty_map["PM"], subject_id=subject_map["3270623L"]),  # PM Lab batch
        FacultySubject(faculty_id=faculty_map["NS"], subject_id=subject_map["3270623L"]),  # NS Lab batch
        FacultySubject(faculty_id=faculty_map["TS"], subject_id=subject_map["3270622L"]),  # TS Lab batch
        FacultySubject(faculty_id=faculty_map["HSP"], subject_id=subject_map["3270622L"]), # HSP Lab batch

        # AIML subjects
        FacultySubject(faculty_id=faculty_map["AB"], subject_id=subject_map["3280621"]),   # AB teaches NLP
        FacultySubject(faculty_id=faculty_map["TS"], subject_id=subject_map["3280622"]),   # TS teaches Image Processing
        FacultySubject(faculty_id=faculty_map["PM"], subject_id=subject_map["3280623"]),   # PM teaches Deep Learning
        FacultySubject(faculty_id=faculty_map["TS"], subject_id=subject_map["3280624"]),   # TS supervises Minor Project
        FacultySubject(faculty_id=faculty_map["PM"], subject_id=subject_map["3280623L"]),  # PM Lab batch
        FacultySubject(faculty_id=faculty_map["RES"], subject_id=subject_map["3280623L"]), # RES Lab batch
        FacultySubject(faculty_id=faculty_map["HSP"], subject_id=subject_map["3280622L"]), # HSP Lab batch
        FacultySubject(faculty_id=faculty_map["MC"], subject_id=subject_map["3280622L"]),  # MC Lab batch

        # Common - IPR
        FacultySubject(faculty_id=faculty_map["RRS"], subject_id=subject_map["1000007"]),
        FacultySubject(faculty_id=faculty_map["PT"], subject_id=subject_map["1000007"]),
    ]
    db.add_all(faculty_subject_data)
    db.flush()

    # ──────────────────────────────────────────────
    #  CLASS ↔ SUBJECT ASSIGNMENTS (with hours/week)
    # ──────────────────────────────────────────────
    class_subject_data = [
        # AIR-VI
        ClassSubject(class_id=class_map["AIR-VI"], subject_id=subject_map["3240621"], hours_per_week=3),
        ClassSubject(class_id=class_map["AIR-VI"], subject_id=subject_map["3240622"], hours_per_week=3),
        ClassSubject(class_id=class_map["AIR-VI"], subject_id=subject_map["3240623"], hours_per_week=3),
        ClassSubject(class_id=class_map["AIR-VI"], subject_id=subject_map["3240624"], hours_per_week=2),
        ClassSubject(class_id=class_map["AIR-VI"], subject_id=subject_map["3240623L"], hours_per_week=2),
        ClassSubject(class_id=class_map["AIR-VI"], subject_id=subject_map["1000007"], hours_per_week=1),

        # AI&DS-VI
        ClassSubject(class_id=class_map["AI&DS-VI"], subject_id=subject_map["3270621"], hours_per_week=3),
        ClassSubject(class_id=class_map["AI&DS-VI"], subject_id=subject_map["3270622"], hours_per_week=3),
        ClassSubject(class_id=class_map["AI&DS-VI"], subject_id=subject_map["3270623"], hours_per_week=3),
        ClassSubject(class_id=class_map["AI&DS-VI"], subject_id=subject_map["3270624"], hours_per_week=2),
        ClassSubject(class_id=class_map["AI&DS-VI"], subject_id=subject_map["3270623L"], hours_per_week=2),
        ClassSubject(class_id=class_map["AI&DS-VI"], subject_id=subject_map["3270622L"], hours_per_week=2),
        ClassSubject(class_id=class_map["AI&DS-VI"], subject_id=subject_map["1000007"], hours_per_week=1),

        # AIML-VI
        ClassSubject(class_id=class_map["AIML-VI"], subject_id=subject_map["3280621"], hours_per_week=3),
        ClassSubject(class_id=class_map["AIML-VI"], subject_id=subject_map["3280622"], hours_per_week=3),
        ClassSubject(class_id=class_map["AIML-VI"], subject_id=subject_map["3280623"], hours_per_week=3),
        ClassSubject(class_id=class_map["AIML-VI"], subject_id=subject_map["3280624"], hours_per_week=2),
        ClassSubject(class_id=class_map["AIML-VI"], subject_id=subject_map["3280623L"], hours_per_week=2),
        ClassSubject(class_id=class_map["AIML-VI"], subject_id=subject_map["3280622L"], hours_per_week=2),
        ClassSubject(class_id=class_map["AIML-VI"], subject_id=subject_map["1000007"], hours_per_week=1),
    ]
    db.add_all(class_subject_data)

    db.commit()
    db.close()
    print("  ✅ Database seeded successfully with 6th Sem data!")
    print(f"     → {len(faculty_data)} Faculty members")
    print(f"     → {len(subjects_data)} Subjects")
    print(f"     → {len(rooms_data)} Rooms")
    print(f"     → {len(classes_data)} Classes")
    print(f"     → {len(faculty_subject_data)} Faculty-Subject assignments")
    print(f"     → {len(class_subject_data)} Class-Subject assignments")
