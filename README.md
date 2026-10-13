# PlaceTrack 🎯
### Intelligent Job & Placement Tracker with AI Resume Matching

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.15-red?style=flat)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker_Compose-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Swagger](https://img.shields.io/badge/OpenAPI_3.0-Swagger_UI-85EA2D?style=flat&logo=swagger&logoColor=black)](http://127.0.0.1:8000/api/docs/)
[![Pytest](https://img.shields.io/badge/Tests-27_Passed-success?style=flat&logo=pytest&logoColor=white)](https://pytest.org/)

**PlaceTrack** is a full-stack campus placement and job application management platform built with Python and Django. Designed for higher education placement cells and recruiting teams, PlaceTrack features automated **AI resume parsing**, **skill compatibility scoring**, and **interactive placement analytics**.

---

## 📸 Screenshots

| Login | Student Dashboard |
|---|---|
| ![Login](docs/screenshots/login.png) | ![Dashboard](docs/screenshots/dashboard.png) |

| Jobs with Match Scores | AI Resume Matcher |
|---|---|
| ![Jobs](docs/screenshots/jobs.png) | ![AI Resume Matcher](docs/screenshots/resume-match.png) |

| Applicants (Admin) | Admin Analytics Overview |
|---|---|
| ![Applicants](docs/screenshots/applicants.png) | ![Admin Analytics Overview](docs/screenshots/overview.png) |

**Interactive Swagger API Docs**

![Swagger API Documentation](docs/screenshots/swagger.png)

## 🌟 Key Features

### 1. Role-Based Access Control (RBAC) & Dual-Portal Login
- **Dual-Portal Authentication**: Dedicated side-by-side **Student Login** and **Placement Admin Login** cards on a single responsive interface (`/accounts/login/`). Enforces strict role checking before session creation, card-scoped error feedback, and credential preservation.
- **Students**: Self-register, manage their active resume, browse openings, view match scores, and track submitted applications.
- **Placement Admins**: Provisioned by superusers. Access recruitment analytics, create/manage job openings, review candidate resumes, and update hiring statuses.
- Enforced at both view level (`@student_required`, `@admin_required`) and API permission level (`IsPlacementAdmin`, `IsStudentUser`, `IsAdminOrReadOnly`).

### 2. AI Resume Parsing & Skill Matching Engine
- **Document Support**: Parses text from text-based **PDF** and **TXT** files (Max 5 MB limit).
- **Quality Checks**: Detects and rejects empty or scanned image PDFs with clear user feedback.
- **Skill Compatibility Scoring**: Matches applicant qualifications against job requirements using tokenized boundary analysis.
- **Detailed Skill Insights**: Provides percentage match scores, lists **matched skills** (✓), and pinpoints **missing skills** (✗).

### 3. Application Lifecycle & Live Status Pipeline
- **One-Click Apply**: Records the candidate's exact match score at time of application.
- **Single Application Constraint**: Database `UniqueConstraint` prevents accidental duplicate applications for the same position.
- **Visual Status Tracker**: 4-stage pipeline for students:
  $$\text{Applied} \longrightarrow \text{Shortlisted} \longrightarrow \text{Interview} \longrightarrow \text{Selected}$$
- **Asynchronous Live Updates**: Admins change applicant statuses in real-time using vanilla JavaScript `fetch()` without full-page reloads.

### 4. Admin Analytics Dashboard (Chart.js)
- **4 Key Stat Cards**: Open Jobs, Total Applications, Shortlisted/Beyond, and Selected.
- **Applications per Company**: Vertical bar chart illustrating applicant interest across employers.
- **Top Missing Skills**: Horizontal bar chart identifying curriculum skill gaps across the candidate pool.
- Powered by a dedicated asynchronous JSON analytics endpoint (`/accounts/api/analytics/`).

### 5. Production-Grade REST API with Swagger Docs
- Built with **Django REST Framework (DRF)** and **Token Authentication**.
- Full CRUD capabilities for jobs and applications with role-based serialization.
- Interactive OpenAPI 3.0 documentation powered by **drf-spectacular**:
  - Swagger UI: [`/api/docs/`](http://127.0.0.1:8000/api/docs/)
  - ReDoc: [`/api/redoc/`](http://127.0.0.1:8000/api/redoc/)

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, Django 5.1, Django REST Framework
- **Production Server & Static Files**: Gunicorn WSGI, WhiteNoise
- **Database**: PostgreSQL 16 (Docker/Production), SQLite 3 (Local Development)
- **Document Processing**: `pypdf`, `python-docx`
- **Frontend**: Clean Semantic HTML5, CSS3, Vanilla JavaScript (No heavyweight JS frameworks required)
- **Data Visualization**: Chart.js
- **API Documentation**: OpenAPI 3.0 via `drf-spectacular`
- **Containerization**: Docker, Docker Compose
- **Automated Testing**: `pytest`, `pytest-django`

---

## 🚀 Getting Started

### Option 1: Quickstart with Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pernirishendrachowdary07/placetrack.git
   cd placetrack
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```

3. **Launch the services:**
   ```bash
   docker compose up --build
   ```
   *The container automatically runs database migrations, seeds 8 sample jobs, and launches Gunicorn on `http://localhost:8000`.*

---

### Option 2: Local Development Setup (Without Docker)

1. **Create and activate virtual environment:**
   ```powershell
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   ```bash
   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   *(For local SQLite, keep `DB_ENGINE=sqlite` in `.env`)*

4. **Run migrations and seed sample jobs:**
   ```bash
   python manage.py migrate
   python manage.py seed_jobs
   ```

5. **Start the development server:**
   ```bash
   python manage.py runserver
   ```
   Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

---

## 🔑 Demo Credentials

| Role | Username | Password | Dashboard URL |
|---|---|---|---|
| **Placement Admin** | `admin` | `admin123` | [Admin Overview](http://127.0.0.1:8000/accounts/admin-overview/) |
| **Student** | `alice_student` | `StrongP@ssw0rd123` | [Student Dashboard](http://127.0.0.1:8000/accounts/student-dashboard/) |
| **Student (Self-register)** | Any | Direct Signup | [Student Register](http://127.0.0.1:8000/accounts/register/) |

---

## 📖 API Documentation & Example

Interactive documentation is available at:
- **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **ReDoc**: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)

### Example: Authenticating and Querying Jobs

1. **Obtain API Token:**
   ```bash
   curl -X POST http://127.0.0.1:8000/api/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "alice_student", "password": "StrongP@ssw0rd123"}'
   ```
   *Response:*
   ```json
   {
     "token": "4955b2d56d78709ec55d7f76ca096735e5d32c02",
     "user_id": 2,
     "username": "alice_student",
     "email": "alice@example.com",
     "role": "student"
   }
   ```

2. **Query Jobs with Token:**
   ```bash
   curl -H "Authorization: Token <YOUR_TOKEN>" http://127.0.0.1:8000/api/jobs/
   ```

---

## 🧪 Running Automated Tests

Run the complete test suite using `pytest`:
```bash
pytest
```
*Executes all 27 integration tests across text extraction, match calculations, dual-card authentication, role-based access control, and duplicate application constraints.*

---

## 📁 Project Structure

```text
RATE MY RESUME/
├── accounts/               # User authentication, custom User model, and RBAC
│   ├── decorators.py       # @student_required, @admin_required
│   ├── forms.py            # Student registration & login forms
│   └── views.py            # Auth views & Chart.js JSON analytics endpoint
├── jobs/                   # Job listings, application tracker & REST APIs
│   ├── api_permissions.py  # DRF role permissions
│   ├── api_views.py        # ViewSets for Jobs & Applications
│   ├── serializers.py      # DRF serializers
│   └── views.py            # Job CRUD, search & async status endpoints
├── resumes/                # Resume management & AI matching engine
│   ├── forms.py            # File upload validation (PDF/TXT, 5 MB limit)
│   ├── matcher.py          # extract_text() & match() logic
│   └── views.py            # Resume upload & compatibility views
├── placetrack/             # Project settings, WSGI/ASGI, URLs & API router
├── static/                 # Static CSS and Vanilla JavaScript
│   ├── css/style.css       # Clean responsive styling
│   └── js/                 # Asynchronous fetch scripts (applicants.js, overview_charts.js)
├── templates/              # Django templates (base.html, accounts/, jobs/, resumes/)
├── tests/                  # Pytest test suite (matcher, RBAC, applications)
├── Dockerfile              # Production Docker image definition
├── docker-compose.yml      # Multi-container orchestration (Django + PostgreSQL)
├── .env.example            # Environment variables template
├── pytest.ini              # Pytest configuration
└── requirements.txt        # Pinned project dependencies
```

---

## 📄 License
This project is open-source and available under the MIT License.
