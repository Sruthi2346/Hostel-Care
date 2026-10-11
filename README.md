# Hostel Care — Smart Hostel Management System

A student hostel management demo built with HTML/CSS/JavaScript, FastAPI, SQLAlchemy and MySQL.

## Features
- Separate student, staff and admin dashboards with role-based sidebar navigation
- Student self-registration and admin-created student admissions
- Admin-created staff/admin accounts and bootstrap admin login
- Hostel rooms, capacity, occupancy and room allocation/transfer history
- Date-wise morning/evening hostel attendance by room; duplicate attendance is updated
- Student sick/rest reports and return status
- Maintenance requests, staff assignment, status updates and request history
- Leave/outpass requests and staff/admin approval
- Visitor entry/exit register
- Notices and announcements
- Reports, room occupancy summary, attendance CSV export and admin audit log
- Password hashing, JWT login, API role checks

## 1. MySQL setup
In MySQL Workbench, run:

```sql
CREATE DATABASE hostel_care_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Do not use or delete your older project database. This app uses a separate database.

## 2. Configure environment
Copy `backend/.env.example` to `backend/.env` and update `DATABASE_URL` with your MySQL username/password. Set a unique `SECRET_KEY` and change `BOOTSTRAP_ADMIN_PASSWORD` before use. Never commit `.env` to GitHub.

Example secret generation command:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the output into `SECRET_KEY` in `.env`.

## 3. Install and run backend (Windows PowerShell)
Open VS Code terminal in the project folder:

```powershell
cd backend
python --version
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again. Keep the backend terminal running.

Check:
- Health: http://127.0.0.1:8000/api/health
- Interactive API docs: http://127.0.0.1:8000/docs

On first successful startup, the app creates its tables and bootstrap admin account. It does not migrate existing tables; use the dedicated fresh database above.

## 4. Run frontend
Install the VS Code **Live Server** extension if needed. Open `frontend/index.html`, right-click and choose **Open with Live Server**. Use an HTTP URL such as `http://127.0.0.1:5500/index.html`, never a `file:///...` URL. If Live Server uses a different port, add that exact origin to `FRONTEND_ORIGINS` in `backend/.env`, then restart Uvicorn.

## 5. Initial admin
Use the values configured in `backend/.env`:
- Email: `BOOTSTRAP_ADMIN_EMAIL`
- Password: `BOOTSTRAP_ADMIN_PASSWORD`

Default example is `admin@hostel.local` / `ChangeMe123!`; change it before using the app. Bootstrap admin is created only if that email does not already exist. Changing `.env` later does not reset an existing account password.

## 6. Suggested end-to-end test
1. Login as bootstrap admin.
2. Admin → Staff & Accounts: create a staff account with a password of at least 8 characters.
3. Admin → Student Admission: create a student; or use Student Register on login page.
4. Admin → Hostel Rooms: add a room with capacity.
5. Admin → Room Allocation: assign student to room and academic year.
6. Logout, login as student. Submit a maintenance request, a sick/rest report and an outpass request.
7. Login as admin, assign the maintenance request to staff and review reports/notices/outpass.
8. Login as staff, open Assigned Maintenance and update status to In Progress then Resolved; mark attendance; view rest reports and approve/reject outpass.
9. Login as student again and verify request status/history and attendance.
10. Admin → Reports & Analytics: check occupancy and download attendance CSV.

## Notes / limitations
- This is a local academic demo, not a production-ready residence system. Before deployment, add migrations (Alembic), stronger audit/retention policies, password reset, rate limiting, HTTPS, backups and institutional approval workflows.
- Student registration is open in this demo. For a real hostel, disable public self-registration and allow admission only through an authorized administrator.
- Staff can mark attendance for all students in this demo; add warden/room-level permissions if required.
- CSV export includes student data. Store and share it securely.
- `create_all()` creates missing tables but does not alter old schemas. Use a new empty database for this project.
