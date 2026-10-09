# Placement Portal Application

A comprehensive web-based placement management system for institutes to manage campus recruitment activities involving companies and students.

## Features

### Admin (Institute Placement Cell)
- **Dashboard**: View total students, companies, drives, and applications
- **Company Management**: Approve/reject company registrations, blacklist/activate companies
- **Drive Management**: Approve/reject placement drives
- **Student Management**: View all students, blacklist/activate students
- **Search**: Search companies and students by name, ID, or contact
- **Statistics**: View placement statistics by branch and company
- **Reports**: View all applications and placement history

### Company
- **Registration**: Register company profile with details
- **Dashboard**: View company details, created drives, and applicant counts
- **Drive Management**: Create, edit, close, and delete placement drives
- **Application Management**: View student applications, shortlist, select, or reject students
- **Offer Letters**: Generate offer letters for selected students

### Student
- **Registration**: Self-register with profile details
- **Dashboard**: View approved placement drives with eligibility filtering
- **Applications**: Apply for placement drives, view application status
- **Profile Management**: Edit profile, upload resume
- **History**: View complete placement application history
- **Export**: Export application history as CSV (async job)

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: VueJS 3
- **Styling**: Bootstrap 5
- **Database**: SQLite
- **Caching**: Redis
- **Background Jobs**: Celery with Redis broker
- **Authentication**: JWT (JSON Web Tokens)

## Prerequisites

- Python 3.8+
- Node.js 16+
- Redis Server
- Git

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Placement-Portal-App
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 4. Redis Setup

Make sure Redis server is running on your system:

```bash
# On Windows (using Redis for Windows)
redis-server

# On Linux/Mac
redis-server
```

### 5. Environment Configuration

The application uses default configuration in `backend/config.py`. For production, create a `.env` file:

```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///placement_portal.db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Running the Application

### 1. Start Redis Server

```bash
redis-server
```

### 2. Start Celery Worker (for background jobs)

Open a new terminal:

```bash
cd backend
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On Linux/Mac

celery -A app.tasks.celery_config worker --loglevel=info
```

### 3. Start Celery Beat (for scheduled jobs)

Open another terminal:

```bash
cd backend
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate

celery -A app.tasks.celery_config beat --loglevel=info
```

### 4. Start Flask Backend

Open another terminal:

```bash
cd backend
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate

python run.py
```

The backend will run on `http://localhost:5000`

### 5. Start VueJS Frontend

Open another terminal:

```bash
cd frontend
npm run serve
```

The frontend will run on `http://localhost:8080`

## Default Admin Credentials

- **Email**: admin@placementportal.com
- **Password**: admin123

⚠️ **Important**: Change the default admin password in production!

## Database

The SQLite database is created automatically when you first run the application. The database file is `placement_portal.db` in the backend directory.

### Database Schema

- **User**: Stores user credentials and role (admin/company/student)
- **Company**: Company profile details
- **Student**: Student profile details
- **Drive**: Placement/job drive details
- **Application**: Student applications to drives

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user
- `POST /api/auth/change-password` - Change password

### Admin
- `GET /api/admin/dashboard` - Dashboard statistics
- `GET /api/admin/companies` - List companies
- `POST /api/admin/companies/{id}/approve` - Approve company
- `POST /api/admin/companies/{id}/reject` - Reject company
- `POST /api/admin/companies/{id}/blacklist` - Blacklist company
- `POST /api/admin/companies/{id}/activate` - Activate company
- `GET /api/admin/students` - List students
- `POST /api/admin/students/{id}/blacklist` - Blacklist student
- `POST /api/admin/students/{id}/activate` - Activate student
- `GET /api/admin/drives` - List drives
- `POST /api/admin/drives/{id}/approve` - Approve drive
- `POST /api/admin/drives/{id}/reject` - Reject drive
- `GET /api/admin/applications` - List all applications
- `GET /api/admin/statistics` - Get statistics

### Company
- `GET /api/company/profile` - Get company profile
- `PUT /api/company/profile` - Update company profile
- `GET /api/company/dashboard` - Dashboard statistics
- `POST /api/company/drives` - Create drive
- `GET /api/company/drives` - List company drives
- `PUT /api/company/drives/{id}` - Update drive
- `PUT /api/company/drives/{id}/close` - Close drive
- `DELETE /api/company/drives/{id}` - Delete drive
- `GET /api/company/drives/{id}/applications` - Get drive applications
- `POST /api/company/applications/{id}/shortlist` - Shortlist student
- `POST /api/company/applications/{id}/select` - Select student
- `POST /api/company/applications/{id}/reject` - Reject student
- `GET /api/company/applications/{id}/offer-letter` - Generate offer letter

### Student
- `GET /api/student/profile` - Get student profile
- `PUT /api/student/profile` - Update student profile
- `POST /api/student/resume` - Upload resume
- `GET /api/student/dashboard` - Dashboard data
- `GET /api/student/applications` - Get applications
- `POST /api/student/applications/export` - Export applications (CSV)
- `GET /api/student/applications/export/status/{task_id}` - Get export status
- `GET /api/student/applications/download/{filename}` - Download export

### Drive
- `GET /api/drive/` - List all approved drives
- `GET /api/drive/{id}` - Get drive details
- `POST /api/drive/{id}/apply` - Apply for drive
- `GET /api/drive/search` - Search drives

## Background Jobs

### Daily Reminders
- Runs every 24 hours
- Sends reminders to students about upcoming application deadlines
- Configured via Celery Beat

### Monthly Activity Report
- Runs on the 1st of every month
- Generates HTML report for admin with placement statistics
- Includes drive counts, application counts, and selection data

### CSV Export (User-triggered)
- Triggered by students from dashboard
- Exports application history to CSV
- Async job with status tracking

## Project Structure

```
Placement-Portal-App/
├── backend/
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API routes
│   │   ├── tasks/          # Celery tasks
│   │   └── utils/          # Utility functions
│   ├── config.py           # Configuration
│   ├── run.py              # Flask entry point
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── public/             # Static files
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── views/         # Page views
│   │   ├── router/        # Vue Router
│   │   ├── api.js         # API client
│   │   ├── App.vue        # Root component
│   │   └── main.js        # Entry point
│   └── package.json       # Node dependencies
├── uploads/               # File uploads
└── requirements.txt       # Python dependencies
```

## Development Notes

### Adding New Features

1. **Backend**: Add routes in `backend/app/routes/`, models in `backend/app/models/`
2. **Frontend**: Add views in `frontend/src/views/`, components in `frontend/src/components/`
3. **API**: Update `frontend/src/api.js` with new endpoints

### Testing

- Backend: Use Flask's test client or Postman
- Frontend: Test manually in browser

### Troubleshooting

**Redis Connection Error**: Ensure Redis server is running
```bash
redis-server
```

**Database Lock Error**: Close any database viewers (DB Browser) before running the app

**CORS Error**: Ensure Flask-CORS is properly configured in `backend/app/__init__.py`

## License

This project is created for educational purposes.

## Contact

For issues or questions, please contact the development team.
