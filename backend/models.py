"""
AI Timetable Generator — Database Models
SQLAlchemy ORM models + Pydantic schemas for API validation.
"""
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

Base = declarative_base()

# ═══════════════════════════════════════════════════════════
#  SQLAlchemy ORM Models (Database Tables)
# ═══════════════════════════════════════════════════════════

class Faculty(Base):
    """Faculty/Teacher entity"""
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    department = Column(String(100), default="Centre for AI")
    designation = Column(String(100), default="Assistant Professor")
    max_hours_per_day = Column(Integer, default=6)
    email = Column(String(200), default="")

    # Relationships
    subject_assignments = relationship("FacultySubject", back_populates="faculty", cascade="all, delete-orphan")
    timetable_entries = relationship("TimetableEntry", back_populates="faculty")


class Subject(Base):
    """Subject/Course entity"""
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    subject_type = Column(String(20), default="theory")  # theory, lab, project
    hours_per_week = Column(Integer, default=3)
    color = Column(String(7), default="#667eea")  # Hex color for UI display

    # Relationships
    faculty_assignments = relationship("FacultySubject", back_populates="subject", cascade="all, delete-orphan")
    class_assignments = relationship("ClassSubject", back_populates="subject", cascade="all, delete-orphan")
    timetable_entries = relationship("TimetableEntry", back_populates="subject")


class Room(Base):
    """Room/Venue entity"""
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    capacity = Column(Integer, default=60)
    is_lab = Column(Boolean, default=False)
    building = Column(String(100), default="New Academic Block")

    # Relationships
    timetable_entries = relationship("TimetableEntry", back_populates="room")


class ClassSection(Base):
    """Class/Section entity (e.g., AIR VI Sem)"""
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    branch = Column(String(100), nullable=False)
    semester = Column(Integer, nullable=False)
    student_count = Column(Integer, default=60)

    # Relationships
    subject_assignments = relationship("ClassSubject", back_populates="class_section", cascade="all, delete-orphan")
    timetable_entries = relationship("TimetableEntry", back_populates="class_section")


class FacultySubject(Base):
    """Many-to-Many: Which faculty can teach which subject"""
    __tablename__ = "faculty_subjects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    faculty_id = Column(Integer, ForeignKey("faculty.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)

    faculty = relationship("Faculty", back_populates="subject_assignments")
    subject = relationship("Subject", back_populates="faculty_assignments")


class ClassSubject(Base):
    """Many-to-Many: Which subjects are taught to which class, with hours"""
    __tablename__ = "class_subjects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    hours_per_week = Column(Integer, default=3)

    class_section = relationship("ClassSection", back_populates="subject_assignments")
    subject = relationship("Subject", back_populates="class_assignments")


class Timetable(Base):
    """Generated timetable metadata"""
    __tablename__ = "timetables"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    created_at = Column(String(50), default="")
    fitness_score = Column(Float, default=0.0)
    hard_violations = Column(Integer, default=0)
    soft_score = Column(Float, default=0.0)
    generation_time = Column(Float, default=0.0)  # seconds
    status = Column(String(20), default="completed")  # generating, completed, failed

    # Relationships
    entries = relationship("TimetableEntry", back_populates="timetable", cascade="all, delete-orphan")


class TimetableEntry(Base):
    """Individual slot assignment in a generated timetable"""
    __tablename__ = "timetable_entries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timetable_id = Column(Integer, ForeignKey("timetables.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    day = Column(Integer, nullable=False)       # 0=Monday, 1=Tuesday, ..., 5=Saturday
    time_slot = Column(Integer, nullable=False)  # 0-6 (7 time slots)

    # Relationships
    timetable = relationship("Timetable", back_populates="entries")
    class_section = relationship("ClassSection", back_populates="timetable_entries")
    faculty = relationship("Faculty", back_populates="timetable_entries")
    subject = relationship("Subject", back_populates="timetable_entries")
    room = relationship("Room", back_populates="timetable_entries")


# ═══════════════════════════════════════════════════════════
#  Pydantic Schemas (API Request/Response Validation)
# ═══════════════════════════════════════════════════════════

class FacultyCreate(BaseModel):
    name: str
    code: str
    department: str = "Centre for AI"
    designation: str = "Assistant Professor"
    max_hours_per_day: int = 6
    email: str = ""

class FacultyResponse(BaseModel):
    id: int
    name: str
    code: str
    department: str
    designation: str
    max_hours_per_day: int
    email: str

    class Config:
        from_attributes = True


class SubjectCreate(BaseModel):
    name: str
    code: str
    subject_type: str = "theory"
    hours_per_week: int = 3
    color: str = "#667eea"

class SubjectResponse(BaseModel):
    id: int
    name: str
    code: str
    subject_type: str
    hours_per_week: int
    color: str

    class Config:
        from_attributes = True


class RoomCreate(BaseModel):
    name: str
    capacity: int = 60
    is_lab: bool = False
    building: str = "New Academic Block"

class RoomResponse(BaseModel):
    id: int
    name: str
    capacity: int
    is_lab: bool
    building: str

    class Config:
        from_attributes = True


class ClassCreate(BaseModel):
    name: str
    branch: str
    semester: int
    student_count: int = 60

class ClassResponse(BaseModel):
    id: int
    name: str
    branch: str
    semester: int
    student_count: int

    class Config:
        from_attributes = True


class FacultySubjectCreate(BaseModel):
    faculty_id: int
    subject_id: int

class FacultySubjectResponse(BaseModel):
    id: int
    faculty_id: int
    subject_id: int
    faculty_name: Optional[str] = None
    subject_name: Optional[str] = None

    class Config:
        from_attributes = True


class ClassSubjectCreate(BaseModel):
    class_id: int
    subject_id: int
    hours_per_week: int = 3

class ClassSubjectResponse(BaseModel):
    id: int
    class_id: int
    subject_id: int
    hours_per_week: int
    class_name: Optional[str] = None
    subject_name: Optional[str] = None

    class Config:
        from_attributes = True


class GenerateRequest(BaseModel):
    name: str = "Generated Timetable"
    class_ids: Optional[List[int]] = None  # None = all classes
    max_iterations: int = 2000
    population_size: int = 50


class TimetableEntryResponse(BaseModel):
    id: int
    class_id: int
    faculty_id: int
    subject_id: int
    room_id: int
    day: int
    time_slot: int
    class_name: Optional[str] = None
    faculty_name: Optional[str] = None
    faculty_code: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    subject_color: Optional[str] = None
    room_name: Optional[str] = None

    class Config:
        from_attributes = True


class TimetableResponse(BaseModel):
    id: int
    name: str
    created_at: str
    fitness_score: float
    hard_violations: int
    soft_score: float
    generation_time: float
    status: str
    entries: List[TimetableEntryResponse] = []

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total_faculty: int
    total_subjects: int
    total_rooms: int
    total_classes: int
    total_timetables: int
    total_assignments: int
    lab_rooms: int
    theory_subjects: int
    lab_subjects: int
