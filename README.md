# Coderr Backend

A Django-based backend project for the Coderr application.

## 📋 Project Overview

This is a Django project configured with Django REST Framework and CORS support. It provides a foundation for building REST API endpoints.

## 🛠️ Technology Stack

- **Framework**: Django 6.0.2
- **API Framework**: Django REST Framework 3.16.1
- **Database**: SQLite (development)
- **CORS**: django-cors-headers 4.9.0
- **Environment Management**: python-dotenv 1.2.1
- **Python Version**: Python 3.x (recommended: 3.8+)

## 📦 Dependencies

```txt
asgiref==3.11.1
Django==6.0.2
django-cors-headers==4.9.0
djangorestframework==3.16.1
python-dotenv==1.2.1
sqlparse==0.5.5
tzdata==2025.3
```

## 🚀 Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python Package Manager)

### 1. Clone the repository

```bash
git clone <repository-url>
cd Coderr
```

### 2. Create and activate virtual environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Sensitive data is managed in a `.env` file. **Create a .env file based on .env.example:**

```bash
# Copy .env.example to .env
cp .env.example .env

# Windows:
copy .env.example .env
```

**Then edit the .env file and adjust the values:**
- Generate a new `SECRET_KEY` (see Step 5)
- Configure `ALLOWED_HOSTS` for your domain
- Set `DEBUG=False` for production

**⚠️ Security Notes:**
- **NEVER** commit the `.env` file to Git (already included in .gitignore)
- **Production:** Generate a new SECRET_KEY for production
- **Production:** Set `DEBUG=False`
- **Production:** Configure `ALLOWED_HOSTS` according to your domain
- **Privacy:** Use strong, unique passwords

### Step 5: Generate New SECRET_KEY

**⚠️ IMPORTANT:** Always generate a new SECRET_KEY for your installation:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the generated key and replace `your-secret-key-here` in your `.env` file.

### 6. Run database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create superuser (optional)

```bash
python manage.py createsuperuser
```

### 8. Start development server

```bash
python manage.py runserver
```

The server runs by default on `http://localhost:8000/`

## 🗂️ Project Structure

```
Coderr/
├── core/                  # Main Django configuration
│   ├── asgi.py            # ASGI configuration
│   ├── settings.py        # Django settings
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI configuration
├── .env                   # Environment variables (not in Git)
├── .env.example           # Environment variables example
├── .gitignore            # Git ignore file
├── db.sqlite3            # SQLite database (development)
├── manage.py             # Django management commands
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## 🔧 Available Management Commands

```bash
# Start server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Django shell
python manage.py shell

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic
```

## 🌐 Available Endpoints

### Admin Panel
- `GET /admin/` - Django Admin Interface

*Additional API endpoints will be documented here as they are implemented.*

## 🔐 Configuration Notes

The project is configured with:

- **CORS Headers**: Enabled for cross-origin requests
- **Django REST Framework**: Ready for API development
- **Environment Variables**: Loaded via python-dotenv
- **SQLite Database**: Default development database

Current settings include basic Django apps plus `corsheaders` for CORS support.

## 🚀 Production Considerations

Before deploying to production:

1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Generate a strong `SECRET_KEY`
4. Configure production database
5. Set up static file serving
6. Enable HTTPS