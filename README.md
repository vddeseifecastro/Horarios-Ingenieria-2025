<div align="center">

# 📅 Horarios-Ingenieria-2025
### Academic Schedule Management System

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A full-stack academic schedule management system built for the Faculty of Technical and Agricultural Sciences — Computer Engineering program. Features a dark cyberpunk UI, drag-and-drop schedule builder, intelligent auto-generation, multi-user management, and export to PDF and Excel.

[Report Bug](https://github.com/vddeseifecastro/Horarios-Ingenieria-2025/issues) · [Request Feature](https://github.com/vddeseifecastro/Horarios-Ingenieria-2025/issues)

</div>

---

## 📸 Screenshots

### 🏠 Landing Page

![Landing Page 1](https://github.com/user-attachments/assets/a3b91143-5384-41b6-ab28-915e0ddb5138)

![Landing Page 2](https://github.com/user-attachments/assets/75563bb7-1684-4280-bf36-abfd3683c95d)

### 🔐 Authentication

**Login**

![Login](https://github.com/user-attachments/assets/29bdcf38-50d5-423b-91a6-59a79a1db810)

**Create Account**

![Create Account](https://github.com/user-attachments/assets/776c103c-b0af-444e-9b03-bf9226a659e4)

### 🖥️ Admin Panel

**Dashboard**

![Admin Dashboard](https://github.com/user-attachments/assets/e740cba6-9601-46b7-9c4d-d0a4017580ad)

**Subject Management**

![Subject Management](https://github.com/user-attachments/assets/8640341e-f21e-483d-a9ef-2237bf314567)

**New Subject**

![New Subject](https://github.com/user-attachments/assets/6625d577-9036-4c72-af6f-cb540b6266f6)

**Teacher Management**

![Teacher Management](https://github.com/user-attachments/assets/f3b4fc79-3272-400c-9c64-2e0621712bd9)

**New Teacher**

![New Teacher](https://github.com/user-attachments/assets/8124d7f6-5af1-4a62-ac6e-e00842e173c8)

**Academic Shift Settings**

![Academic Shift Settings](https://github.com/user-attachments/assets/ab33727d-ef84-4c3c-8d01-bc0af159d5c7)

**User Management**

![User Management](https://github.com/user-attachments/assets/17f12e90-2026-4cb8-aedd-7bd69e34e9df)

### 🗓️ Schedule Management

**Schedule List**

![Schedule Management](https://github.com/user-attachments/assets/a04a32da-262c-4ebb-8ef9-247a607f9719)

**Create New Schedule**

![Create New Schedule](https://github.com/user-attachments/assets/05cd9c9e-6abe-491e-8f6d-33668b3cf1c8)

**Schedule Editor**

![Schedule Editor 1](https://github.com/user-attachments/assets/a25bcf34-a261-454c-a53f-6952ecdb7652)

![Schedule Editor 2](https://github.com/user-attachments/assets/d077129c-1be6-4f95-89d8-16a41c0a3461)

**Full Semester View (Admin)**

![Full Semester View Admin](https://github.com/user-attachments/assets/fcdea6e4-b32a-4c07-8bcb-641ad5ba7dd3)

### 👤 User Panel

**User Dashboard**

![User Dashboard](https://github.com/user-attachments/assets/315cf632-97e1-4bcf-9bfd-82bd690a7702)

**Full Semester View (User)**

![Full Semester View User](https://github.com/user-attachments/assets/41f05688-0dfa-4114-aa93-70fe70784827)

---

## ✨ Features

### 🛠️ Admin
- Secure login with session management and password hashing (Werkzeug)
- **Change password** directly from the dashboard
- Full **subject CRUD** — code, name, academic year, semester, assigned teacher, contact hours, color tag
- Full **teacher CRUD** — personal data, specialty, active/inactive status
- **Academic shift configuration** — define custom morning/afternoon teaching time blocks
- **Drag-and-drop schedule editor** — visually assign teachers and subjects to daily slots across the full semester
- **Intelligent auto-generation** — automatically fills morning slots (Monday–Thursday, class weeks only) based on each subject's required contact hours, respecting a maximum of 2 slots per subject per week and skipping exam weeks entirely
- Create and manage multiple academic schedules simultaneously
- Export schedules to **PDF** and **Excel**
- **User management panel** — create, edit, activate/deactivate, and delete user accounts
- Admin-only access to all sensitive endpoints

### 👤 Student / User
- View personal academic schedule by week
- Full semester view with all subjects and assigned teachers
- Public registration (role locked to `user`)

### 🔒 Security
- `SECRET_KEY` loaded exclusively from `.env` — server refuses to start if not set
- `DEBUG` mode controlled via environment variable, defaults to `false`
- Passwords hashed with Werkzeug's `generate_password_hash`
- Role-based access control on every admin route and API endpoint
- Public registration forces `role='user'` — privilege escalation via API is not possible
- Admin cannot delete or deactivate their own account
- `.env` and `*.db` files excluded from version control

---

## 🖥️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, Flask 3.0, Flask-SQLAlchemy, Flask-Login, Flask-CORS |
| Frontend | HTML5, CSS3, Bootstrap 5, Font Awesome 6, Dragula.js |
| Auth | Flask-Login, Werkzeug password hashing |
| Database | SQLite via Flask-SQLAlchemy |
| Exports | pandas + openpyxl (Excel), ReportLab (PDF) |
| Config | python-dotenv |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/vddeseifecastro/Horarios-Ingenieria-2025.git
cd Horarios-Ingenieria-2025
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r backend/requirements.txt
```

**4. Create your `.env` file**

Copy the example and fill in your values:
```bash
copy .env.example .env       # Windows
cp .env.example .env         # macOS / Linux
```

Generate a secure secret key:
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
```

Paste the output into your `.env` file:
```env
SECRET_KEY=your_generated_key_here
DEBUG=false
```

**5. Run the server**
```bash
python run.py
```

Open `http://localhost:5000` in your browser.

> On first run, default credentials are printed **once** in the terminal. Change them immediately after logging in.

---

## 📁 Project Structure

```
Horarios-Ingenieria-2025/
├── .env                        ← Your local secrets (never committed)
├── .env.example                ← Template for environment variables
├── .gitignore
├── run.py                      ← Entry point
├── backend/
│   ├── app.py                  ← Flask app, all routes and API endpoints
│   ├── auth.py                 ← Authentication logic
│   ├── config.py               ← Config class, loads SECRET_KEY from .env
│   ├── database.py             ← SQLAlchemy setup
│   ├── models.py               ← Database models (Usuario, Asignatura, Profesor, Horario, Turno)
│   ├── excel_parser.py         ← Excel import/export logic
│   ├── pdf_generator.py        ← PDF generation with ReportLab
│   └── requirements.txt
├── frontend/
│   ├── login.html
│   ├── registro.html           ← Public registration
│   ├── admin/
│   │   ├── dashboard.html      ← Admin home + quick actions
│   │   ├── asignaturas.html    ← Subject management
│   │   ├── profesores.html     ← Teacher management
│   │   ├── turnos.html         ← Academic shift configuration
│   │   ├── horarios.html       ← Schedule list
│   │   ├── crear_horario.html  ← New schedule form
│   │   ├── editar_horario.html ← Drag-and-drop schedule editor
│   │   ├── exportar.html       ← PDF / Excel export
│   │   └── usuarios.html       ← User management panel
│   ├── user/
│   │   ├── dashboard.html      ← User home
│   │   ├── horario-view.html   ← Weekly schedule view
│   │   └── horario_semestral_completo.html
│   ├── css/
│   └── js/
├── database/
│   └── horarios.db             ← SQLite database (not committed)
└── uploads/                    ← Generated files (not committed)
    ├── excel/
    └── pdf/
```

---

## 🌱 Roadmap

- [ ] Full ES / EN language switcher across the entire UI
- [ ] Schedule conflict detection (teacher double-booking alert)
- [ ] Email notifications on account creation
- [ ] Print-friendly schedule view
- [ ] Dark / light theme toggle
- [ ] Deploy with Gunicorn + Nginx

---

## 👨‍💻 Author

**Victor Dominic Deseife Castro**

[![GitHub](https://img.shields.io/badge/GitHub-vddeseifecastro-181717?style=for-the-badge&logo=github)](https://github.com/vddeseifecastro)

---

<div align="center">
  <p>Built with ❤️ by Victor Dominic Deseife Castro</p>
  <p>⭐ Star this repo if you found it useful!</p>
</div>