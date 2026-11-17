# TaskFlow — Flask + MySQL starter

A small, responsive To-Do application built with Flask, SQLAlchemy and a database URL.
It is configured to use local MySQL first and can later be switched to Neon PostgreSQL.

## 1. Requirements

- Python 3.10+
- MySQL Server running locally
- VS Code (recommended)

## 2. Create the local MySQL database

Open MySQL Workbench or the MySQL command line and run:

```sql
CREATE DATABASE taskflow_db;
```

The Flask app creates the `task` table automatically on its first run.

## 3. Set up the Python project

Open this folder in VS Code. In the terminal:

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and update `YOUR_PASSWORD` with your local MySQL password.
If your MySQL username is not `root`, update that too.

If your password contains special URL characters such as `@`, `#`, `/` or `:`,
URL-encode the password before putting it in the connection URL.

## 4. Run the app

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser.

Check the database connection at http://127.0.0.1:5000/health.
A successful response looks like:

```json
{"database":"connected","status":"ok"}
```

## 5. Switch to Neon PostgreSQL later

When you create a Neon project, copy its connection string. In your deployed
environment variables, set:

```text
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
SECRET_KEY=your-long-random-secret
```

The application normalizes `postgresql://` to the Psycopg 3 SQLAlchemy driver.
Keep the Neon connection string private. Do not commit `.env` to GitHub.

The local MySQL database is not automatically copied to Neon. If you want to
keep existing tasks/data, export and migrate the data separately.

## 6. Deployment note

This repository includes a Vercel Python entry point (`api/index.py`) and
`vercel.json` for trying the Flask app on Vercel. Vercel's serverless functions
need a reachable cloud database; they cannot connect to MySQL running only on
your personal laptop once deployed.

Use a cloud database URL in Vercel Project Settings → Environment Variables.
Test the deployment and current Vercel Python/runtime support before relying on
it for a public service.

## Important limitations of this first version

- This starter has one shared task list: anyone who can open the website can
  see, add, complete or delete tasks. Do not publish it for real public use yet.
- Before inviting the public, we should add user registration/login so each
  person sees only their own tasks, plus CSRF protection and rate limiting.
- Never put database credentials in Python source code or commit `.env`.
