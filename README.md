<div align="center">

# 📅 Horarios-Ingenieria-2025
### Academic Schedule Management System

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A full-stack academic schedule management system built for the Faculty of Technical and Agricultural Sciences — Computer Engineering program. Features a dark cyberpunk UI, drag-and-drop schedule builder, multi-user management, and export capabilities to PDF and Excel.

[Report Bug](https://github.com/vddeseifecastro/Horarios-Ingenieria-2025/issues) · [Request Feature](https://github.com/vddeseifecastro/Horarios-Ingenieria-2025/issues)

</div>

---

## 📸 Screenshots

### 🔐 Authentication

**Login**

![Login](https://placehold.co/900x500/0a0e17/00ffff?text=Login+Screenshot)

**Register**

![Register](https://placehold.co/900x500/0a0e17/00ffff?text=Register+Screenshot)

### 🖥️ Admin Dashboard

![Admin Dashboard](https://placehold.co/900x500/0a0e17/00ffff?text=Admin+Dashboard+Screenshot)

### 📚 Subject Management

![Subjects](https://placehold.co/900x500/0a0e17/00ffff?text=Subjects+Screenshot)

### 👨‍🏫 Professor Management

![Professors](https://placehold.co/900x500/0a0e17/00ffff?text=Professors+Screenshot)

### 🗓️ Schedule Builder (Drag & Drop)

![Schedule Builder](https://placehold.co/900x500/0a0e17/00ffff?text=Schedule+Builder+Screenshot)

### 👤 User Dashboard

![User Dashboard](https://placehold.co/900x500/0a0e17/00ffff?text=User+Dashboard+Screenshot)

### 👥 User Management

![User Management](https://placehold.co/900x500/0a0e17/00ffff?text=User+Management+Screenshot)

---

## ✨ Features

### 🛠️ Admin
- Secure login with session management and password hashing (Werkzeug)
- Full **subject (asignatura) CRUD** — code, name, academic year, semester, assigned professor, hours, color tag
- Full **professor CRUD** — personal data, specialty, active/inactive status
- **Time slot (turno) management** — define custom teaching time blocks
- **Drag-and-drop schedule builder** — assign professors and subjects to daily slots visually
- **Automatic schedule generation** based on configured subjects and professors
- Create and manage multiple academic schedules simultaneously
- Export schedules to **PDF** and **Excel**
- **User management panel** — create, edit, activate/deactivate, and delete users
- **Change password** directly from the dashboard
- Admin-only access to debug and sensitive endpoints

### 👤 User
- View assigned academic schedule
- Full semester view
- Public registration form (role locked to `user`)

### 🔒 Security
- `SECRET_KEY` loaded from `.env` — server refuses to start if not set
- `DEBUG` mode controlled via environment variable, defaults to `false`
- Passwords hashed with Werkzeug's `generate_password_hash`
- Role-based access control on all admin routes and API endpoints
- Registration endpoint forces `role='user'` — cannot escalate to admin via API
- Admin cannot delete or deactivate their own account
- `.env` and `*.db` files excluded from version control via `.gitignore`

---

## 🖥️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, Flask 3.0, Flask-SQLAlchemy, Flask-Login, Flask-CORS |
| Frontend | HTML5, CSS3, Bootstrap 5, Font Awesome 6, Dragula.js |
| Auth | Flask-Login, Werkzeug password hashing |
| Database | SQLite via Flask-SQLAlchemy |
| Exports | openpyxl (Excel), ReportLab (PDF) |
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

Copy the example file and fill in your values:
```bash
copy .env.example .env       # Windows
cp .env.example .env         # macOS / Linux
```

Generate a secure secret key:
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
```

Paste the output into your `.env` file. It should look like:
```env
SECRET_KEY=a3f8c2d1e4b7a9f0c6e2d5b8a1f4c7e0a3d6b9c2f5e8a1d4b7c0e3f6a9d2b5
DEBUG=false
```

**5. Run the server**
```bash
python run.py
```

The app will be available at `http://localhost:5000`

> On first run, default credentials are printed once in the terminal. **Change them immediately** after logging in.

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
│   │   ├── profesores.html     ← Professor management
│   │   ├── turnos.html         ← Time slot configuration
│   │   ├── horarios.html       ← Schedule list
│   │   ├── crear_horario.html  ← New schedule form
│   │   ├── editar_horario.html ← Drag-and-drop schedule builder
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
├── uploads/
│   ├── excel/
│   └── pdf/
└── sounds/
```

---

## 🌱 Roadmap

- [ ] Full ES / EN language switcher across the entire UI
- [ ] Email notifications on account creation
- [ ] Deploy with Gunicorn + Nginx
- [ ] Schedule conflict detection (professor double-booking alert)
- [ ] Print-friendly schedule view
- [ ] Dark / light theme toggle

---

## 👨‍💻 Author

**Victor Dominic Deseife Castro**

[![GitHub](https://img.shields.io/badge/GitHub-vddeseifecastro-181717?style=for-the-badge&logo=github)](https://github.com/vddeseifecastro)

---

<div align="center">
  <p>Built with ❤️ by Victor Dominic Deseife Castro</p>
  <p>⭐ Star this repo if you found it useful!</p>
</div>