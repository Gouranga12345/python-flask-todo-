
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Flask configuration
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "local-development-secret-key"
)

database_url = os.getenv("DATABASE_URL", "").strip()

# Normalize PostgreSQL URLs for cloud deployment
if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql://", 1
    )

if database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    database_url or "sqlite:///taskflow.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True
}

db = SQLAlchemy(app)


# =====================================
# DATABASE MODEL
# =====================================

class Task(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    is_done = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )


# =====================================
# HOME PAGE
# =====================================

@app.get("/")
def index():

    selected = request.args.get("filter", "all")

    query = Task.query.order_by(
        Task.created_at.desc()
    )

    if selected == "active":
        query = query.filter_by(is_done=False)

    elif selected == "completed":
        query = query.filter_by(is_done=True)

    else:
        selected = "all"

    tasks = query.all()

    total = Task.query.count()

    completed = Task.query.filter_by(
        is_done=True
    ).count()

    active = total - completed

    return render_template(
        "index.html",
        tasks=tasks,
        selected=selected,
        total=total,
        completed=completed,
        active=active
    )


# =====================================
# ADD TASK
# =====================================

@app.post("/tasks")
def add_task():

    title = request.form.get("title", "").strip()

    print("ADD TASK ROUTE CALLED:", title, flush=True)

    if not title:

        flash(
            "Please enter a task before adding it.",
            "error"
        )

    elif len(title) > 200:

        flash(
            "Task titles must be 200 characters or fewer.",
            "error"
        )

    else:

        try:

            new_task = Task(title=title)

            db.session.add(new_task)

            db.session.commit()

            print(
                "TASK INSERTED SUCCESSFULLY. ID:",
                new_task.id,
                flush=True
            )

            flash(
                "Task added. Nice progress!",
                "success"
            )

        except Exception:

            db.session.rollback()

            app.logger.exception(
                "Error while inserting task into database"
            )

            flash(
                "Unable to save task. Check the server terminal.",
                "error"
            )

    return redirect(url_for("index"))


# =====================================
# MARK TASK COMPLETE / ACTIVE
# =====================================

@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):

    task = db.get_or_404(Task, task_id)

    try:

        task.is_done = not task.is_done

        db.session.commit()

    except Exception:

        db.session.rollback()

        app.logger.exception(
            "Error while updating task"
        )

    return redirect(
        url_for(
            "index",
            filter=request.form.get("filter", "all")
        )
    )


# =====================================
# DELETE TASK
# =====================================

@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):

    task = db.get_or_404(Task, task_id)

    try:

        db.session.delete(task)

        db.session.commit()

        flash(
            "Task deleted.",
            "success"
        )

    except Exception:

        db.session.rollback()

        app.logger.exception(
            "Error while deleting task"
        )

        flash(
            "Unable to delete task.",
            "error"
        )

    return redirect(
        url_for(
            "index",
            filter=request.form.get("filter", "all")
        )
    )


# =====================================
# DATABASE HEALTH CHECK
# =====================================

@app.get("/health")
def health():

    try:

        db.session.execute(text("SELECT 1"))

        return jsonify({
            "status": "ok",
            "database": "connected"
        })

    except Exception:

        db.session.rollback()

        app.logger.exception(
            "Database health check failed"
        )

        return jsonify({
            "status": "error",
            "database": "unavailable"
        }), 503


# =====================================
# DATABASE DIAGNOSTICS
# =====================================

@app.get("/debug-db")
def debug_db():

    try:

        database_name = db.engine.url.render_as_string(
            hide_password=True
        )

        tasks = Task.query.order_by(
            Task.created_at.desc()
        ).all()

        return jsonify({

            "database": database_name,

            "task_count": len(tasks),

            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "is_done": task.is_done
                }
                for task in tasks
            ]

        })

    except Exception:

        db.session.rollback()

        app.logger.exception(
            "Database diagnostic failed"
        )

        return jsonify({
            "status": "error",
            "message": "Database query failed. Check terminal."
        }), 500


# =====================================
# CREATE DATABASE TABLES
# =====================================

with app.app_context():

    db.create_all()

    print("===================================")

    print("TASKFLOW DATABASE INITIALIZED")

    print(
        "DATABASE:",
        db.engine.url.render_as_string(
            hide_password=True
        )
    )

    print(
        "TABLES:",
        db.inspect(db.engine).get_table_names()
    )

    print("===================================")


# =====================================
# RUN APPLICATION
# =====================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=os.getenv(
            "FLASK_DEBUG",
            "false"
        ).lower() == "true"
    )
