# LocalFix

LocalFix is a simple Django project for reporting neighborhood issues.

## First version

This version includes:

- Django project setup
- session cookie authentication
- user registration
- login and logout
- user profile with a basic role field
- Latvian and English language switching
- PostgreSQL database settings through environment variables

## Run locally

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/lv/
```

## Database

The project uses PostgreSQL.

Create a database named `localfix`, then set these environment variables if your local values are different from the defaults:

```text
POSTGRES_DB=localfix
POSTGRES_USER=localfix
POSTGRES_PASSWORD=localfix
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```
