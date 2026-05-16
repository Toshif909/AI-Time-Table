"""
AI Timetable Generator — FastAPI Server
Complete REST API with CRUD operations for all entities,
AI timetable generation, conflict detection, and CSV export.
"""
import os
import csv
import io
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import create_tables, seed_database, get_db, SessionLocal
from .models import (
    Faculty, Subject, Room, ClassSection, FacultySubject, ClassSubject,
    Timetable, TimetableEntry,
    FacultyCreate, FacultyResponse,
    SubjectCreate, SubjectResponse,
    RoomCreate, RoomResponse,
    ClassCreate, ClassResponse,
    FacultySubjectCreate, FacultySubjectResponse,
    ClassSubjectCreate, ClassSubjectResponse,
    GenerateRequest, TimetableResponse, TimetableEntryResponse,
    StatsResponse,
)
from .ai_engine import TimetableGenerator, detect_conflicts, DAYS, TIME_SLOTS

# ═══════════════════════════════════════════════════════════
#  APPLICATION SETUP
# ═══════════════════════════════════════════════════════════

app = FastAPI(
    title="AI Timetable Generator",
    description="AI-Powered Timetable Generation System - Centre for Artificial Intelligence",
    version="1.0.0",
)

# CORS (allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (frontend)
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")


@app.on_event("startup")
def startup():
    """Initialize database and seed data on startup."""
    create_tables()
    seed_database()
    print("  🚀 Server started successfully!")


# ═══════════════════════════════════════════════════════════
#  FRONTEND SERVING
# ═══════════════════════════════════════════════════════════

# Mount static files for CSS, JS, assets
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend():
    """Serve the main SPA HTML page."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


# ═══════════════════════════════════════════════════════════
#  STATS API
# ═══════════════════════════════════════════════════════════

@app.get("/api/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    return StatsResponse(
        total_faculty=db.query(Faculty).count(),
        total_subjects=db.query(Subject).count(),
        total_rooms=db.query(Room).count(),
        total_classes=db.query(ClassSection).count(),
        total_timetables=db.query(Timetable).count(),
        total_assignments=db.query(FacultySubject).count() + db.query(ClassSubject).count(),
        lab_rooms=db.query(Room).filter(Room.is_lab == True).count(),
        theory_subjects=db.query(Subject).filter(Subject.subject_type == "theory").count(),
        lab_subjects=db.query(Subject).filter(Subject.subject_type.in_(["lab", "project"])).count(),
    )


# ═══════════════════════════════════════════════════════════
#  FACULTY CRUD
# ═══════════════════════════════════════════════════════════

@app.get("/api/faculty", response_model=List[FacultyResponse])
def list_faculty(db: Session = Depends(get_db)):
    return db.query(Faculty).order_by(Faculty.name).all()


@app.post("/api/faculty", response_model=FacultyResponse)
def create_faculty(data: FacultyCreate, db: Session = Depends(get_db)):
    if db.query(Faculty).filter(Faculty.code == data.code).first():
        raise HTTPException(400, f"Faculty with code '{data.code}' already exists")
    faculty = Faculty(**data.model_dump())
    db.add(faculty)
    db.commit()
    db.refresh(faculty)
    return faculty


@app.put("/api/faculty/{faculty_id}", response_model=FacultyResponse)
def update_faculty(faculty_id: int, data: FacultyCreate, db: Session = Depends(get_db)):
    faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
    if not faculty:
        raise HTTPException(404, "Faculty not found")
    for key, value in data.model_dump().items():
        setattr(faculty, key, value)
    db.commit()
    db.refresh(faculty)
    return faculty


@app.delete("/api/faculty/{faculty_id}")
def delete_faculty(faculty_id: int, db: Session = Depends(get_db)):
    faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
    if not faculty:
        raise HTTPException(404, "Faculty not found")
    db.delete(faculty)
    db.commit()
    return {"message": "Faculty deleted successfully"}


# ═══════════════════════════════════════════════════════════
#  SUBJECTS CRUD
# ═══════════════════════════════════════════════════════════

@app.get("/api/subjects", response_model=List[SubjectResponse])
def list_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).order_by(Subject.name).all()


@app.post("/api/subjects", response_model=SubjectResponse)
def create_subject(data: SubjectCreate, db: Session = Depends(get_db)):
    if db.query(Subject).filter(Subject.code == data.code).first():
        raise HTTPException(400, f"Subject with code '{data.code}' already exists")
    subject = Subject(**data.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@app.put("/api/subjects/{subject_id}", response_model=SubjectResponse)
def update_subject(subject_id: int, data: SubjectCreate, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(404, "Subject not found")
    for key, value in data.model_dump().items():
        setattr(subject, key, value)
    db.commit()
    db.refresh(subject)
    return subject


@app.delete("/api/subjects/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(404, "Subject not found")
    db.delete(subject)
    db.commit()
    return {"message": "Subject deleted successfully"}


# ═══════════════════════════════════════════════════════════
#  ROOMS CRUD
# ═══════════════════════════════════════════════════════════

@app.get("/api/rooms", response_model=List[RoomResponse])
def list_rooms(db: Session = Depends(get_db)):
    return db.query(Room).order_by(Room.name).all()


@app.post("/api/rooms", response_model=RoomResponse)
def create_room(data: RoomCreate, db: Session = Depends(get_db)):
    room = Room(**data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@app.put("/api/rooms/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, data: RoomCreate, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Room not found")
    for key, value in data.model_dump().items():
        setattr(room, key, value)
    db.commit()
    db.refresh(room)
    return room


@app.delete("/api/rooms/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Room not found")
    db.delete(room)
    db.commit()
    return {"message": "Room deleted successfully"}


# ═══════════════════════════════════════════════════════════
#  CLASSES CRUD
# ═══════════════════════════════════════════════════════════

@app.get("/api/classes", response_model=List[ClassResponse])
def list_classes(db: Session = Depends(get_db)):
    return db.query(ClassSection).order_by(ClassSection.name).all()


@app.post("/api/classes", response_model=ClassResponse)
def create_class(data: ClassCreate, db: Session = Depends(get_db)):
    cls = ClassSection(**data.model_dump())
    db.add(cls)
    db.commit()
    db.refresh(cls)
    return cls


@app.put("/api/classes/{class_id}", response_model=ClassResponse)
def update_class(class_id: int, data: ClassCreate, db: Session = Depends(get_db)):
    cls = db.query(ClassSection).filter(ClassSection.id == class_id).first()
    if not cls:
        raise HTTPException(404, "Class not found")
    for key, value in data.model_dump().items():
        setattr(cls, key, value)
    db.commit()
    db.refresh(cls)
    return cls


@app.delete("/api/classes/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db)):
    cls = db.query(ClassSection).filter(ClassSection.id == class_id).first()
    if not cls:
        raise HTTPException(404, "Class not found")
    db.delete(cls)
    db.commit()
    return {"message": "Class deleted successfully"}


# ═══════════════════════════════════════════════════════════
#  FACULTY-SUBJECT ASSIGNMENTS
# ═══════════════════════════════════════════════════════════

@app.get("/api/faculty-subjects")
def list_faculty_subjects(db: Session = Depends(get_db)):
    assignments = db.query(FacultySubject).all()
    result = []
    for a in assignments:
        faculty = db.query(Faculty).filter(Faculty.id == a.faculty_id).first()
        subject = db.query(Subject).filter(Subject.id == a.subject_id).first()
        result.append({
            "id": a.id,
            "faculty_id": a.faculty_id,
            "subject_id": a.subject_id,
            "faculty_name": faculty.name if faculty else "",
            "faculty_code": faculty.code if faculty else "",
            "subject_name": subject.name if subject else "",
            "subject_code": subject.code if subject else "",
        })
    return result


@app.post("/api/faculty-subjects")
def create_faculty_subject(data: FacultySubjectCreate, db: Session = Depends(get_db)):
    # Check for duplicates
    existing = db.query(FacultySubject).filter(
        FacultySubject.faculty_id == data.faculty_id,
        FacultySubject.subject_id == data.subject_id,
    ).first()
    if existing:
        raise HTTPException(400, "This assignment already exists")
    assignment = FacultySubject(**data.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return {"id": assignment.id, "message": "Assignment created"}


@app.delete("/api/faculty-subjects/{assignment_id}")
def delete_faculty_subject(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(FacultySubject).filter(FacultySubject.id == assignment_id).first()
    if not assignment:
        raise HTTPException(404, "Assignment not found")
    db.delete(assignment)
    db.commit()
    return {"message": "Assignment deleted"}


# ═══════════════════════════════════════════════════════════
#  CLASS-SUBJECT ASSIGNMENTS
# ═══════════════════════════════════════════════════════════

@app.get("/api/class-subjects")
def list_class_subjects(db: Session = Depends(get_db)):
    assignments = db.query(ClassSubject).all()
    result = []
    for a in assignments:
        cls = db.query(ClassSection).filter(ClassSection.id == a.class_id).first()
        subject = db.query(Subject).filter(Subject.id == a.subject_id).first()
        result.append({
            "id": a.id,
            "class_id": a.class_id,
            "subject_id": a.subject_id,
            "hours_per_week": a.hours_per_week,
            "class_name": cls.name if cls else "",
            "subject_name": subject.name if subject else "",
            "subject_code": subject.code if subject else "",
        })
    return result


@app.post("/api/class-subjects")
def create_class_subject(data: ClassSubjectCreate, db: Session = Depends(get_db)):
    existing = db.query(ClassSubject).filter(
        ClassSubject.class_id == data.class_id,
        ClassSubject.subject_id == data.subject_id,
    ).first()
    if existing:
        raise HTTPException(400, "This assignment already exists")
    assignment = ClassSubject(**data.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return {"id": assignment.id, "message": "Assignment created"}


@app.delete("/api/class-subjects/{assignment_id}")
def delete_class_subject(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(ClassSubject).filter(ClassSubject.id == assignment_id).first()
    if not assignment:
        raise HTTPException(404, "Assignment not found")
    db.delete(assignment)
    db.commit()
    return {"message": "Assignment deleted"}


# ═══════════════════════════════════════════════════════════
#  TIMETABLE GENERATION (AI Engine)
# ═══════════════════════════════════════════════════════════

@app.post("/api/generate")
def generate_timetable(request: GenerateRequest, db: Session = Depends(get_db)):
    """
    🧠 AI-Powered Timetable Generation
    Uses CSP (Constraint Satisfaction Problem) solver with
    greedy construction + hill climbing optimization.
    """
    # Gather all data
    faculty_list = [
        {"id": f.id, "name": f.name, "code": f.code, "max_hours_per_day": f.max_hours_per_day}
        for f in db.query(Faculty).all()
    ]
    subject_list = [
        {"id": s.id, "name": s.name, "code": s.code, "subject_type": s.subject_type,
         "hours_per_week": s.hours_per_week, "color": s.color}
        for s in db.query(Subject).all()
    ]
    room_list = [
        {"id": r.id, "name": r.name, "capacity": r.capacity, "is_lab": r.is_lab}
        for r in db.query(Room).all()
    ]

    # Filter classes if specific ones requested
    if request.class_ids:
        class_query = db.query(ClassSection).filter(ClassSection.id.in_(request.class_ids))
    else:
        class_query = db.query(ClassSection)

    class_list = [
        {"id": c.id, "name": c.name, "branch": c.branch, "semester": c.semester}
        for c in class_query.all()
    ]

    if not class_list:
        raise HTTPException(400, "No classes found to generate timetable for")

    class_ids_set = {c["id"] for c in class_list}

    faculty_subjects = [
        {"faculty_id": fs.faculty_id, "subject_id": fs.subject_id}
        for fs in db.query(FacultySubject).all()
    ]
    class_subjects = [
        {"class_id": cs.class_id, "subject_id": cs.subject_id, "hours_per_week": cs.hours_per_week}
        for cs in db.query(ClassSubject).all()
        if cs.class_id in class_ids_set
    ]

    if not class_subjects:
        raise HTTPException(400, "No subject assignments found for selected classes")

    # Run AI engine
    generator = TimetableGenerator(
        faculty=faculty_list,
        subjects=subject_list,
        rooms=room_list,
        classes=class_list,
        faculty_subjects=faculty_subjects,
        class_subjects=class_subjects,
    )

    schedule, fitness, hard_violations, soft_score, gen_time = generator.generate(
        max_iterations=request.max_iterations
    )

    # Detect conflicts
    conflicts = detect_conflicts(schedule)

    # Save to database
    timetable = Timetable(
        name=request.name,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        fitness_score=round(fitness, 2),
        hard_violations=hard_violations,
        soft_score=round(soft_score, 2),
        generation_time=round(gen_time, 3),
        status="completed",
    )
    db.add(timetable)
    db.flush()

    for entry in schedule:
        db_entry = TimetableEntry(
            timetable_id=timetable.id,
            class_id=entry["class_id"],
            faculty_id=entry["faculty_id"],
            subject_id=entry["subject_id"],
            room_id=entry["room_id"],
            day=entry["day"],
            time_slot=entry["time_slot"],
        )
        db.add(db_entry)

    db.commit()
    db.refresh(timetable)

    # Build rich response with names
    entries_response = _build_entries_response(db, timetable.id)

    return {
        "id": timetable.id,
        "name": timetable.name,
        "created_at": timetable.created_at,
        "fitness_score": timetable.fitness_score,
        "hard_violations": timetable.hard_violations,
        "soft_score": timetable.soft_score,
        "generation_time": timetable.generation_time,
        "status": timetable.status,
        "entries": entries_response,
        "conflicts": conflicts,
        "total_entries": len(schedule),
    }


# ═══════════════════════════════════════════════════════════
#  TIMETABLE RETRIEVAL & MANAGEMENT
# ═══════════════════════════════════════════════════════════

@app.get("/api/timetables")
def list_timetables(db: Session = Depends(get_db)):
    """List all generated timetables."""
    timetables = db.query(Timetable).order_by(Timetable.id.desc()).all()
    result = []
    for tt in timetables:
        entry_count = db.query(TimetableEntry).filter(TimetableEntry.timetable_id == tt.id).count()
        result.append({
            "id": tt.id,
            "name": tt.name,
            "created_at": tt.created_at,
            "fitness_score": tt.fitness_score,
            "hard_violations": tt.hard_violations,
            "soft_score": tt.soft_score,
            "generation_time": tt.generation_time,
            "status": tt.status,
            "entry_count": entry_count,
        })
    return result


@app.get("/api/timetables/{timetable_id}")
def get_timetable(timetable_id: int, db: Session = Depends(get_db)):
    """Get a specific timetable with all entries (enriched with names)."""
    timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not timetable:
        raise HTTPException(404, "Timetable not found")

    entries = _build_entries_response(db, timetable_id)

    return {
        "id": timetable.id,
        "name": timetable.name,
        "created_at": timetable.created_at,
        "fitness_score": timetable.fitness_score,
        "hard_violations": timetable.hard_violations,
        "soft_score": timetable.soft_score,
        "generation_time": timetable.generation_time,
        "status": timetable.status,
        "entries": entries,
    }


@app.delete("/api/timetables/{timetable_id}")
def delete_timetable(timetable_id: int, db: Session = Depends(get_db)):
    timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not timetable:
        raise HTTPException(404, "Timetable not found")
    db.delete(timetable)
    db.commit()
    return {"message": "Timetable deleted successfully"}


# ═══════════════════════════════════════════════════════════
#  EXPORT (CSV)
# ═══════════════════════════════════════════════════════════

@app.get("/api/timetables/{timetable_id}/export/csv")
def export_timetable_csv(timetable_id: int, class_id: Optional[int] = None,
                          db: Session = Depends(get_db)):
    """Export timetable as CSV."""
    timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not timetable:
        raise HTTPException(404, "Timetable not found")

    entries_query = db.query(TimetableEntry).filter(TimetableEntry.timetable_id == timetable_id)
    if class_id:
        entries_query = entries_query.filter(TimetableEntry.class_id == class_id)

    entries = entries_query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Day", "Time Slot", "Class", "Subject", "Faculty", "Room"])

    for entry in entries:
        cls = db.query(ClassSection).filter(ClassSection.id == entry.class_id).first()
        subject = db.query(Subject).filter(Subject.id == entry.subject_id).first()
        faculty = db.query(Faculty).filter(Faculty.id == entry.faculty_id).first()
        room = db.query(Room).filter(Room.id == entry.room_id).first()

        writer.writerow([
            DAYS[entry.day] if entry.day < len(DAYS) else entry.day,
            TIME_SLOTS[entry.time_slot] if entry.time_slot < len(TIME_SLOTS) else entry.time_slot,
            cls.name if cls else entry.class_id,
            f"{subject.name} ({subject.code})" if subject else entry.subject_id,
            f"{faculty.name} ({faculty.code})" if faculty else entry.faculty_id,
            room.name if room else entry.room_id,
        ])

    output.seek(0)
    filename = f"timetable_{timetable_id}.csv"
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ═══════════════════════════════════════════════════════════
#  CONFLICT DETECTION API
# ═══════════════════════════════════════════════════════════

@app.get("/api/timetables/{timetable_id}/conflicts")
def get_timetable_conflicts(timetable_id: int, db: Session = Depends(get_db)):
    """Analyze a generated timetable for conflicts."""
    timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not timetable:
        raise HTTPException(404, "Timetable not found")

    entries = db.query(TimetableEntry).filter(TimetableEntry.timetable_id == timetable_id).all()
    schedule = [
        {
            "class_id": e.class_id,
            "faculty_id": e.faculty_id,
            "subject_id": e.subject_id,
            "room_id": e.room_id,
            "day": e.day,
            "time_slot": e.time_slot,
        }
        for e in entries
    ]

    conflicts = detect_conflicts(schedule)
    return {"conflicts": conflicts, "total": len(conflicts)}


# ═══════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════

def _build_entries_response(db: Session, timetable_id: int) -> List[dict]:
    """Build a rich entry list with human-readable names."""
    entries = db.query(TimetableEntry).filter(
        TimetableEntry.timetable_id == timetable_id
    ).all()

    result = []
    for e in entries:
        cls = db.query(ClassSection).filter(ClassSection.id == e.class_id).first()
        faculty = db.query(Faculty).filter(Faculty.id == e.faculty_id).first()
        subject = db.query(Subject).filter(Subject.id == e.subject_id).first()
        room = db.query(Room).filter(Room.id == e.room_id).first()

        result.append({
            "id": e.id,
            "class_id": e.class_id,
            "faculty_id": e.faculty_id,
            "subject_id": e.subject_id,
            "room_id": e.room_id,
            "day": e.day,
            "time_slot": e.time_slot,
            "class_name": cls.name if cls else "",
            "faculty_name": faculty.name if faculty else "",
            "faculty_code": faculty.code if faculty else "",
            "subject_name": subject.name if subject else "",
            "subject_code": subject.code if subject else "",
            "subject_color": subject.color if subject else "#667eea",
            "subject_type": subject.subject_type if subject else "theory",
            "room_name": room.name if room else "",
        })

    return result


# ═══════════════════════════════════════════════════════════
#  CONSTANTS API (for frontend)
# ═══════════════════════════════════════════════════════════

@app.get("/api/constants")
def get_constants():
    """Return scheduling constants for the frontend."""
    return {
        "days": DAYS,
        "time_slots": TIME_SLOTS,
        "subject_types": ["theory", "lab", "project"],
        "subject_colors": [
            "#667eea", "#06b6d4", "#8b5cf6", "#10b981",
            "#f59e0b", "#ec4899", "#ef4444", "#6b7280",
            "#22d3ee", "#a78bfa", "#34d399", "#fb923c",
        ],
    }
