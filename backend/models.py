from datetime import datetime, date
from sqlalchemy import String, Integer, Boolean, DateTime, Date, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(190), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="student") # student, staff, admin
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    student: Mapped["StudentProfile"] = relationship(back_populates="user", uselist=False)

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    student_number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    department: Mapped[str] = mapped_column(String(100), default="Not specified")
    admission_year: Mapped[int] = mapped_column(Integer)
    study_year: Mapped[int] = mapped_column(Integer, default=1)
    guardian_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    guardian_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    hostel_name: Mapped[str] = mapped_column(String(100), default="Main Hostel")
    user: Mapped[User] = relationship(back_populates="student")

class Room(Base):
    __tablename__ = "rooms"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hostel_name: Mapped[str] = mapped_column(String(100), default="Main Hostel")
    block: Mapped[str] = mapped_column(String(50), default="A")
    room_number: Mapped[str] = mapped_column(String(20), index=True)
    floor: Mapped[int] = mapped_column(Integer, default=1)
    capacity: Mapped[int] = mapped_column(Integer, default=4)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    __table_args__ = (UniqueConstraint("hostel_name", "block", "room_number", name="uq_room"),)

class RoomAllocation(Base):
    __tablename__ = "room_allocations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    academic_year: Mapped[str] = mapped_column(String(20))
    bed_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, default=date.today)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)

class Attendance(Base):
    __tablename__ = "attendance_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id"), nullable=True)
    attendance_date: Mapped[date] = mapped_column(Date, default=date.today, index=True)
    session: Mapped[str] = mapped_column(String(20)) # Morning, Evening
    status: Mapped[str] = mapped_column(String(20), default="Present")
    marked_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("student_user_id", "attendance_date", "session", name="uq_attendance_session"),)

class RestReport(Base):
    __tablename__ = "rest_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    reported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expected_return: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reason: Mapped[str] = mapped_column(String(100), default="Not feeling well")
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Resting") # Resting, Returned, Closed
    confirmed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    category: Mapped[str] = mapped_column(String(60))
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20), default="Normal")
    status: Mapped[str] = mapped_column(String(30), default="Submitted")
    assigned_staff_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class RequestHistory(Base):
    __tablename__ = "request_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("maintenance_requests.id"), index=True)
    changed_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(30))
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Outpass(Base):
    __tablename__ = "outpasses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    destination: Mapped[str] = mapped_column(String(200))
    reason: Mapped[str] = mapped_column(String(300))
    leave_at: Mapped[datetime] = mapped_column(DateTime)
    expected_return: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="Pending")
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Visitor(Base):
    __tablename__ = "visitors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visitor_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    student_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    purpose: Mapped[str] = mapped_column(String(250))
    entry_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    exit_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    recorded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

class Notice(Base):
    __tablename__ = "notices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    message: Mapped[str] = mapped_column(Text)
    audience: Mapped[str] = mapped_column(String(20), default="all")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(160))
    details: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
