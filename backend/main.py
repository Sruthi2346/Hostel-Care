import os
from datetime import datetime, date
from typing import Any
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from pydantic import BaseModel, EmailStr, Field
from database import Base, engine, get_db, SessionLocal
from models import User, StudentProfile, Room, RoomAllocation, Attendance, RestReport, MaintenanceRequest, RequestHistory, Outpass, Visitor, Notice, AuditLog
from auth import hash_password, verify_password, create_token, get_current_user, require_roles

load_dotenv()
app = FastAPI(title="Hostel Care API", version="1.0.0", description="Hostel admissions, rooms, attendance, welfare and maintenance")

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5501",
    "http://localhost:5501",
]
print("DEBUG CORS ORIGINS:", repr(origins))
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = None
    student_number: str = Field(min_length=2, max_length=40)
    department: str = "Not specified"
    admission_year: int = Field(ge=2000, le=2100)
    study_year: int = Field(default=1, ge=1, le=8)
    guardian_name: str | None = None
    guardian_phone: str | None = None

class LoginIn(BaseModel):
    email: str
    password: str

class StaffIn(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    phone: str | None = None
    department: str | None = None
    role: str = "staff"

class StudentAdmissionIn(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    student_number: str
    department: str = "Not specified"
    admission_year: int
    study_year: int = 1
    phone: str | None = None
    guardian_name: str | None = None
    guardian_phone: str | None = None

class RoomIn(BaseModel):
    hostel_name: str = "Main Hostel"
    block: str = "A"
    room_number: str
    floor: int = 1
    capacity: int = Field(ge=1, le=20)

class MaintenanceIn(BaseModel):
    category: str
    title: str
    description: str
    priority: str = "Normal"

class RestIn(BaseModel):
    reason: str = "Not feeling well"
    note: str | None = None
    reported_at: datetime | None = None

class OutpassIn(BaseModel):
    destination: str
    reason: str
    leave_at: datetime
    expected_return: datetime

class NoticeIn(BaseModel):
    title: str
    message: str
    audience: str = "all"

def audit(db: Session, actor: User, action: str, details: str = ""):
    db.add(AuditLog(actor_id=actor.id, action=action, details=details[:500] or None))

def user_dict(u: User):
    d = {"id":u.id,"name":u.name,"email":u.email,"role":u.role,"phone":u.phone,"department":u.department,"is_active":u.is_active}
    if u.student:
        p=u.student
        d["student"]={"student_number":p.student_number,"department":p.department,"admission_year":p.admission_year,"study_year":p.study_year,"guardian_name":p.guardian_name,"guardian_phone":p.guardian_phone,"hostel_name":p.hostel_name}
    return d

def room_dict(db: Session, room: Room):
    used = db.scalar(select(func.count(RoomAllocation.id)).where(RoomAllocation.room_id==room.id, RoomAllocation.is_current==True)) or 0
    return {"id":room.id,"hostel_name":room.hostel_name,"block":room.block,"room_number":room.room_number,"floor":room.floor,"capacity":room.capacity,"occupied":used,"available":max(0,room.capacity-used),"is_active":room.is_active}

def request_dict(db: Session, r: MaintenanceRequest):
    student=db.get(User,r.student_user_id); staff=db.get(User,r.assigned_staff_id) if r.assigned_staff_id else None
    return {"id":r.id,"student_user_id":r.student_user_id,"student_name":student.name if student else "Unknown","category":r.category,"title":r.title,"description":r.description,"priority":r.priority,"status":r.status,"assigned_staff_id":r.assigned_staff_id,"assigned_staff_name":staff.name if staff else None,"resolution_note":r.resolution_note,"created_at":r.created_at,"updated_at":r.updated_at,"resolved_at":r.resolved_at}

def student_room(db: Session, student_id: int):
    alloc=db.scalar(select(RoomAllocation).where(RoomAllocation.student_user_id==student_id, RoomAllocation.is_current==True))
    if not alloc: return None
    room=db.get(Room,alloc.room_id)
    return {**room_dict(db,room),"academic_year":alloc.academic_year,"bed_number":alloc.bed_number,"allocation_id":alloc.id} if room else None

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        email=os.getenv("BOOTSTRAP_ADMIN_EMAIL","admin@hostel.local").lower()
        if not db.scalar(select(User).where(User.email==email)):
            db.add(User(name=os.getenv("BOOTSTRAP_ADMIN_NAME","Hostel Admin"),email=email,password_hash=hash_password(os.getenv("BOOTSTRAP_ADMIN_PASSWORD","ChangeMe123!")),role="admin",is_active=True))
            db.commit()

@app.get("/api/health")
def health(db: Session=Depends(get_db)):
    db.execute(select(1))
    return {"status":"ok","database":"connected","app":"Hostel Care"}

@app.post("/api/auth/register")
def register(data: RegisterIn, db: Session=Depends(get_db)):
    email=data.email.lower()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(409,"Email already registered")
    if db.scalar(select(StudentProfile).where(StudentProfile.student_number==data.student_number)): raise HTTPException(409,"Student number already exists")
    u=User(name=data.name,email=email,password_hash=hash_password(data.password),role="student",phone=data.phone,department=data.department)
    db.add(u); db.flush()
    db.add(StudentProfile(user_id=u.id,student_number=data.student_number,department=data.department,admission_year=data.admission_year,study_year=data.study_year,guardian_name=data.guardian_name,guardian_phone=data.guardian_phone))
    audit(db,u,"Student self-registration",data.student_number); db.commit(); db.refresh(u)
    return {"message":"Registration successful. You can login now.","user":user_dict(u)}

@app.post("/api/auth/login")
def login(data: LoginIn, db: Session=Depends(get_db)):
    u=db.scalar(select(User).where(User.email==data.email.lower()))
    if not u or not verify_password(data.password,u.password_hash): raise HTTPException(401,"Incorrect email or password")
    if not u.is_active: raise HTTPException(403,"Account is inactive. Contact hostel admin.")
    return {"access_token":create_token(u),"token_type":"bearer","user":user_dict(u)}

@app.get("/api/auth/me")
def me(user: User=Depends(get_current_user)):
    with SessionLocal() as db: return user_dict(db.get(User,user.id))

@app.get("/api/dashboard")
def dashboard(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    if user.role=="student":
        reqs=list(db.scalars(select(MaintenanceRequest).where(MaintenanceRequest.student_user_id==user.id).order_by(MaintenanceRequest.created_at.desc())))
        att=list(db.scalars(select(Attendance).where(Attendance.student_user_id==user.id).order_by(Attendance.attendance_date.desc()).limit(10)))
        rests=list(db.scalars(select(RestReport).where(RestReport.student_user_id==user.id,RestReport.status=="Resting")))
        return {"role":"student","requests_total":len(reqs),"requests_open":sum(r.status!="Resolved" for r in reqs),"requests_resolved":sum(r.status=="Resolved" for r in reqs),"room":student_room(db,user.id),"active_rest_reports":len(rests),"recent_attendance":[{"date":a.attendance_date,"session":a.session,"status":a.status} for a in att]}
    if user.role=="staff":
        reqs=list(db.scalars(select(MaintenanceRequest).where(MaintenanceRequest.assigned_staff_id==user.id)))
        return {"role":"staff","assigned_total":len(reqs),"open":sum(r.status!="Resolved" for r in reqs),"resolved":sum(r.status=="Resolved" for r in reqs)}
    return {"role":"admin","students":db.scalar(select(func.count(User.id)).where(User.role=="student")) or 0,"staff":db.scalar(select(func.count(User.id)).where(User.role=="staff")) or 0,"rooms":db.scalar(select(func.count(Room.id)).where(Room.is_active==True)) or 0,"requests_total":db.scalar(select(func.count(MaintenanceRequest.id))) or 0,"requests_open":db.scalar(select(func.count(MaintenanceRequest.id)).where(MaintenanceRequest.status!="Resolved")) or 0,"requests_resolved":db.scalar(select(func.count(MaintenanceRequest.id)).where(MaintenanceRequest.status=="Resolved")) or 0,"resting_now":db.scalar(select(func.count(RestReport.id)).where(RestReport.status=="Resting")) or 0}

@app.get("/api/users")
def users(role: str|None=None, user: User=Depends(require_roles("admin")), db: Session=Depends(get_db)):
    q=select(User).order_by(User.name)
    if role: q=q.where(User.role==role)
    return [user_dict(u) for u in db.scalars(q)]

@app.post("/api/admin/users")
def create_user(data: StaffIn, user: User=Depends(require_roles("admin")), db: Session=Depends(get_db)):
    if data.role not in ("staff","admin"): raise HTTPException(400,"Only staff/admin accounts can be created here")
    email=data.email.lower()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(409,"Email already exists")
    u=User(name=data.name,email=email,password_hash=hash_password(data.password),role=data.role,phone=data.phone,department=data.department)
    db.add(u); db.flush(); audit(db,user,"Created account",f"{u.role}: {u.email}"); db.commit(); db.refresh(u)
    return user_dict(u)

@app.post("/api/admin/students")
def admit_student(data: StudentAdmissionIn, user: User=Depends(require_roles("admin")), db: Session=Depends(get_db)):
    if db.scalar(select(User).where(User.email==data.email.lower())): raise HTTPException(409,"Email already exists")
    if db.scalar(select(StudentProfile).where(StudentProfile.student_number==data.student_number)): raise HTTPException(409,"Student number already exists")
    u=User(name=data.name,email=data.email.lower(),password_hash=hash_password(data.password),role="student",phone=data.phone,department=data.department)
    db.add(u); db.flush(); db.add(StudentProfile(user_id=u.id,student_number=data.student_number,department=data.department,admission_year=data.admission_year,study_year=data.study_year,guardian_name=data.guardian_name,guardian_phone=data.guardian_phone))
    audit(db,user,"Admitted student",data.student_number); db.commit(); db.refresh(u); return user_dict(u)

@app.get("/api/rooms")
def rooms(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    if user.role=="student":
        r=student_room(db,user.id); return [r] if r else []
    return [room_dict(db,r) for r in db.scalars(select(Room).order_by(Room.hostel_name,Room.block,Room.room_number))]

@app.post("/api/rooms")
def create_room(data: RoomIn, user: User=Depends(require_roles("admin")), db: Session=Depends(get_db)):
    if db.scalar(select(Room).where(Room.hostel_name==data.hostel_name,Room.block==data.block,Room.room_number==data.room_number)): raise HTTPException(409,"Room already exists")
    r=Room(**data.model_dump()); db.add(r); audit(db,user,"Created room",f"{r.hostel_name} {r.block}-{r.room_number}"); db.commit(); db.refresh(r); return room_dict(db,r)

@app.post("/api/rooms/allocate")
def allocate_room(payload: dict=Body(...), user: User=Depends(require_roles("admin")), db: Session=Depends(get_db)):
    student_id=int(payload.get("student_user_id",0)); room_id=int(payload.get("room_id",0)); academic_year=str(payload.get("academic_year","")); bed_number=payload.get("bed_number")
    profile=db.scalar(select(StudentProfile).where(StudentProfile.user_id==student_id)); room=db.get(Room,room_id)
    if not profile or not room: raise HTTPException(404,"Student or room not found")
    existing=db.scalar(select(RoomAllocation).where(RoomAllocation.student_user_id==student_id,RoomAllocation.is_current==True))
    if existing:
        existing.is_current=False; existing.end_date=date.today()
    occupied=db.scalar(select(func.count(RoomAllocation.id)).where(RoomAllocation.room_id==room_id,RoomAllocation.is_current==True)) or 0
    if occupied>=room.capacity: raise HTTPException(409,"Room is full")
    allocation=RoomAllocation(student_user_id=student_id,room_id=room_id,academic_year=academic_year,bed_number=bed_number,is_current=True)
    profile.study_year=int(payload.get("study_year",profile.study_year)); db.add(allocation); audit(db,user,"Allocated room",f"student={profile.student_number}, room={room.room_number}, year={academic_year}"); db.commit(); db.refresh(allocation)
    return {"message":"Room allocation saved","allocation_id":allocation.id}

@app.get("/api/allocations")
def allocations(user: User=Depends(require_roles("admin")), db: Session=Depends(get_db)):
    out=[]
    for a in db.scalars(select(RoomAllocation).order_by(RoomAllocation.start_date.desc())):
        s=db.get(User,a.student_user_id); p=db.scalar(select(StudentProfile).where(StudentProfile.user_id==a.student_user_id)); r=db.get(Room,a.room_id)
        out.append({"id":a.id,"student_user_id":a.student_user_id,"student_name":s.name if s else "","student_number":p.student_number if p else "","study_year":p.study_year if p else None,"room_id":a.room_id,"room_number":r.room_number if r else "","block":r.block if r else "","academic_year":a.academic_year,"bed_number":a.bed_number,"start_date":a.start_date,"end_date":a.end_date,"is_current":a.is_current})
    return out

@app.get("/api/students")
def students(user: User=Depends(require_roles("admin","staff")), db: Session=Depends(get_db)):
    out=[]
    for u in db.scalars(select(User).where(User.role=="student").order_by(User.name)):
        p=u.student; out.append({**user_dict(u),"room":student_room(db,u.id),"student_number":p.student_number if p else None,"study_year":p.study_year if p else None,"admission_year":p.admission_year if p else None})
    return out

@app.get("/api/attendance")
def get_attendance(attendance_date: date|None=None, session: str|None=None, room_id: int|None=None, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    q=select(Attendance).order_by(Attendance.attendance_date.desc())
    if user.role=="student": q=q.where(Attendance.student_user_id==user.id)
    if attendance_date: q=q.where(Attendance.attendance_date==attendance_date)
    if session: q=q.where(Attendance.session==session)
    if room_id: q=q.where(Attendance.room_id==room_id)
    rows=[]
    for a in db.scalars(q.limit(500)):
        s=db.get(User,a.student_user_id); p=s.student if s else None; marker=db.get(User,a.marked_by)
        rows.append({"id":a.id,"student_user_id":a.student_user_id,"student_name":s.name if s else "","student_number":p.student_number if p else "","study_year":p.study_year if p else None,"room_id":a.room_id,"date":a.attendance_date,"session":a.session,"status":a.status,"note":a.note,"marked_by":marker.name if marker else ""})
    return rows

@app.post("/api/attendance/mark")
def mark_attendance(payload: dict=Body(...), user: User=Depends(require_roles("admin","staff")), db: Session=Depends(get_db)):
    d=date.fromisoformat(payload.get("date",date.today().isoformat())); session=payload.get("session","Morning")
    if session not in ("Morning","Evening"): raise HTTPException(400,"Session must be Morning or Evening")
    items=payload.get("records",[])
    for item in items:
        student_id=int(item["student_user_id"]); status=item.get("status","Present")
        if status not in ("Present","Absent","On Rest","On Leave"): raise HTTPException(400,"Invalid attendance status")
        student=db.get(User,student_id)
        if not student or student.role!="student": continue
        alloc=db.scalar(select(RoomAllocation).where(RoomAllocation.student_user_id==student_id,RoomAllocation.is_current==True))
        rec=db.scalar(select(Attendance).where(Attendance.student_user_id==student_id,Attendance.attendance_date==d,Attendance.session==session))
        if not rec:
            rec=Attendance(student_user_id=student_id,room_id=alloc.room_id if alloc else None,attendance_date=d,session=session,status=status,marked_by=user.id,note=item.get("note")); db.add(rec)
        else:
            rec.room_id=alloc.room_id if alloc else None; rec.status=status; rec.marked_by=user.id; rec.note=item.get("note")
    audit(db,user,"Marked attendance",f"{d} {session}, {len(items)} students"); db.commit(); return {"message":"Attendance saved","count":len(items)}

@app.post("/api/rest-reports")
def create_rest(data: RestIn, user: User=Depends(require_roles("student")), db: Session=Depends(get_db)):
    active=db.scalar(select(RestReport).where(RestReport.student_user_id==user.id,RestReport.status=="Resting"))
    if active: raise HTTPException(409,"You already have an active rest report")
    r = RestReport(
    student_user_id=user.id,
    reason=data.reason,
    note=data.note,
    reported_at=data.reported_at or datetime.utcnow()
    ); db.add(r); audit(db,user,"Reported sick/rest",data.reason); db.commit(); db.refresh(r); return {"message":"Rest report sent to hostel staff","id":r.id}

@app.get("/api/rest-reports")
def rest_reports(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    q=select(RestReport).order_by(RestReport.reported_at.desc())
    if user.role=="student": q=q.where(RestReport.student_user_id==user.id)
    out=[]
    for r in db.scalars(q.limit(500)):
        s=db.get(User,r.student_user_id); out.append({"id":r.id,"student_user_id":r.student_user_id,"student_name":s.name if s else "","student_number":s.student.student_number if s and s.student else "","room":student_room(db,r.student_user_id),"reported_at":r.reported_at,"reason":r.reason,"note":r.note,"status":r.status,"returned_at":r.returned_at})
    return out

@app.patch("/api/rest-reports/{report_id}/return")
def close_rest(report_id: int, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    r=db.get(RestReport,report_id)
    if not r: raise HTTPException(404,"Rest report not found")
    if user.role not in ("admin","staff") and r.student_user_id!=user.id: raise HTTPException(403,"Not allowed")
    r.status="Returned"; r.returned_at=datetime.utcnow(); r.confirmed_by=user.id if user.role!="student" else None; audit(db,user,"Marked returned",f"rest report {report_id}"); db.commit(); return {"message":"Return status updated"}

@app.post("/api/maintenance")
def create_maintenance(data: MaintenanceIn, user: User=Depends(require_roles("student")), db: Session=Depends(get_db)):
    r=MaintenanceRequest(student_user_id=user.id,category=data.category,title=data.title,description=data.description,priority=data.priority,status="Submitted")
    db.add(r); db.flush(); db.add(RequestHistory(request_id=r.id,changed_by=user.id,status="Submitted",note="Request submitted")); audit(db,user,"Submitted maintenance request",data.title); db.commit(); db.refresh(r); return request_dict(db,r)

@app.get("/api/maintenance")
def list_maintenance(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    q=select(MaintenanceRequest).order_by(MaintenanceRequest.created_at.desc())
    if user.role=="student": q=q.where(MaintenanceRequest.student_user_id==user.id)
    elif user.role=="staff": q=q.where(MaintenanceRequest.assigned_staff_id==user.id)
    return [request_dict(db,r) for r in db.scalars(q.limit(500))]

@app.get("/api/maintenance/{request_id}/history")
def request_history(request_id: int, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    r=db.get(MaintenanceRequest,request_id)
    if not r: raise HTTPException(404,"Request not found")
    if user.role=="student" and r.student_user_id!=user.id: raise HTTPException(403,"Not allowed")
    if user.role=="staff" and r.assigned_staff_id!=user.id: raise HTTPException(403,"Not allowed")
    return [{"id":h.id,"status":h.status,"note":h.note,"changed_by":db.get(User,h.changed_by).name if db.get(User,h.changed_by) else "","created_at":h.created_at} for h in db.scalars(select(RequestHistory).where(RequestHistory.request_id==request_id).order_by(RequestHistory.created_at))]

@app.patch("/api/maintenance/{request_id}")
def update_maintenance(request_id: int, payload: dict=Body(...), user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    r=db.get(MaintenanceRequest,request_id)
    if not r: raise HTTPException(404,"Request not found")
    if user.role=="student": raise HTTPException(403,"Students cannot update maintenance status")
    if user.role=="staff" and r.assigned_staff_id!=user.id: raise HTTPException(403,"This request is not assigned to you")
    if user.role not in ("admin","staff"): raise HTTPException(403,"Not allowed")
    if "assigned_staff_id" in payload:
        if user.role!="admin": raise HTTPException(403,"Only admin can assign staff")
        sid=payload["assigned_staff_id"]
        if sid is not None:
            staff=db.get(User,int(sid))
            if not staff or staff.role!="staff": raise HTTPException(400,"Select a valid staff account")
        r.assigned_staff_id=int(sid) if sid else None
    if "status" in payload:
        status=payload["status"]
        if status not in ("Submitted","Assigned","In Progress","Resolved"): raise HTTPException(400,"Invalid status")
        r.status=status
        if status=="Resolved": r.resolved_at=datetime.utcnow()
        else: r.resolved_at=None
        db.add(RequestHistory(request_id=r.id,changed_by=user.id,status=status,note=payload.get("resolution_note") or payload.get("note")))
    if "resolution_note" in payload: r.resolution_note=payload["resolution_note"]
    audit(db,user,"Updated maintenance request",f"request={r.id}, status={r.status}"); db.commit(); db.refresh(r); return request_dict(db,r)

@app.post("/api/outpasses")
def create_outpass(data: OutpassIn, user: User=Depends(require_roles("student")), db: Session=Depends(get_db)):
    if data.expected_return < data.leave_at: raise HTTPException(400,"Expected return must be after departure")
    o=Outpass(student_user_id=user.id, destination=data.destination,reason=data.reason,leave_at=data.leave_at,expected_return=data.expected_return); db.add(o); audit(db,user,"Requested outpass",data.destination); db.commit(); db.refresh(o); return {"message":"Outpass request submitted","id":o.id}

@app.get("/api/outpasses")
def list_outpasses(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    q=select(Outpass).order_by(Outpass.created_at.desc())
    if user.role=="student": q=q.where(Outpass.student_user_id==user.id)
    return [{"id":o.id,"student_user_id":o.student_user_id,"student_name":db.get(User,o.student_user_id).name if db.get(User,o.student_user_id) else "","destination":o.destination,"reason":o.reason,"leave_at":o.leave_at,"expected_return":o.expected_return,"status":o.status,"created_at":o.created_at} for o in db.scalars(q.limit(500))]

@app.patch("/api/outpasses/{outpass_id}")
def update_outpass(outpass_id: int, payload: dict=Body(...), user: User=Depends(require_roles("admin","staff")), db: Session=Depends(get_db)):
    o=db.get(Outpass,outpass_id)
    if not o: raise HTTPException(404,"Outpass not found")
    status=payload.get("status")
    if status not in ("Approved","Rejected","Returned"): raise HTTPException(400,"Invalid outpass status")
    o.status=status; o.approved_by=user.id; audit(db,user,"Updated outpass",f"{outpass_id}: {status}"); db.commit(); return {"message":"Outpass updated"}

@app.get("/api/notices")
def list_notices(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    q=select(Notice).where((Notice.audience=="all")|(Notice.audience==user.role)).order_by(Notice.created_at.desc())
    return [{"id":n.id,"title":n.title,"message":n.message,"audience":n.audience,"created_at":n.created_at,"author":db.get(User,n.created_by).name if db.get(User,n.created_by) else ""} for n in db.scalars(q.limit(200))]

@app.post("/api/notices")
def create_notice(data: NoticeIn, user: User=Depends(require_roles("admin")), db: Session=Depends(get_db)):
    if data.audience not in ("all","student","staff","admin"): raise HTTPException(400,"Invalid audience")
    n=Notice(title=data.title,message=data.message,audience=data.audience,created_by=user.id); db.add(n); audit(db,user,"Published notice",data.title); db.commit(); db.refresh(n); return {"message":"Notice published","id":n.id}

@app.get("/api/visitors")
def visitors(user: User=Depends(require_roles("admin","staff")), db: Session=Depends(get_db)):
    return [{"id":v.id,"visitor_name":v.visitor_name,"phone":v.phone,"student_name":db.get(User,v.student_user_id).name if v.student_user_id and db.get(User,v.student_user_id) else "","student_user_id":v.student_user_id,"purpose":v.purpose,"entry_at":v.entry_at,"exit_at":v.exit_at} for v in db.scalars(select(Visitor).order_by(Visitor.entry_at.desc()).limit(500))]

@app.post("/api/visitors")
def create_visitor(payload: dict=Body(...), user: User=Depends(require_roles("admin","staff")), db: Session=Depends(get_db)):
    v=Visitor(visitor_name=payload.get("visitor_name",""),phone=payload.get("phone"),student_user_id=payload.get("student_user_id"),purpose=payload.get("purpose","Visitor"),recorded_by=user.id)
    if not v.visitor_name.strip(): raise HTTPException(400,"Visitor name is required")
    db.add(v); audit(db,user,"Registered visitor",v.visitor_name); db.commit(); db.refresh(v); return {"message":"Visitor entry saved","id":v.id}

@app.patch("/api/visitors/{visitor_id}/checkout")
def visitor_checkout(visitor_id: int, user: User=Depends(require_roles("admin","staff")), db: Session=Depends(get_db)):
    v=db.get(Visitor,visitor_id)
    if not v: raise HTTPException(404,"Visitor not found")
    v.exit_at=datetime.utcnow(); db.commit(); return {"message":"Visitor checkout saved"}

@app.get("/api/reports/summary")
def reports_summary(user: User=Depends(require_roles("admin","staff")), db: Session=Depends(get_db)):
    students=list(db.scalars(select(User).where(User.role=="student")))
    rooms=[room_dict(db,r) for r in db.scalars(select(Room).where(Room.is_active==True))]
    allocations=list(db.scalars(select(RoomAllocation).where(RoomAllocation.is_current==True)))
    reqs=list(db.scalars(select(MaintenanceRequest)))
    attendance=list(db.scalars(select(Attendance)))
    return {"student_count":len(students),"room_count":len(rooms),"allocated_students":len(allocations),"unallocated_students":max(0,len(students)-len({a.student_user_id for a in allocations})),"room_occupancy":rooms,"maintenance":{"total":len(reqs),"open":sum(r.status!="Resolved" for r in reqs),"resolved":sum(r.status=="Resolved" for r in reqs)},"attendance_records":len(attendance),"resting_now":db.scalar(select(func.count(RestReport.id)).where(RestReport.status=="Resting")) or 0}

@app.get("/api/reports/attendance.csv")
def attendance_csv(user: User=Depends(require_roles("admin","staff")), db: Session=Depends(get_db)):
    import csv, io
    buffer=io.StringIO(); writer=csv.writer(buffer); writer.writerow(["Date","Session","Student ID","Student Name","Study Year","Room","Status","Marked By"])
    for a in db.scalars(select(Attendance).order_by(Attendance.attendance_date.desc())):
        s=db.get(User,a.student_user_id); p=s.student if s else None; room=db.get(Room,a.room_id) if a.room_id else None; marker=db.get(User,a.marked_by)
        writer.writerow([a.attendance_date,a.session,p.student_number if p else "",s.name if s else "",p.study_year if p else "",room.room_number if room else "",a.status,marker.name if marker else ""])
    buffer.seek(0); return StreamingResponse(iter([buffer.getvalue()]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=hostel_attendance.csv"})

@app.get("/api/audit-logs")
def audit_logs(user: User=Depends(require_roles("admin")), db: Session=Depends(get_db)):
    return [{"id":a.id,"actor":db.get(User,a.actor_id).name if db.get(User,a.actor_id) else "","action":a.action,"details":a.details,"created_at":a.created_at} for a in db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(300))]
