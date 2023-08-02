import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
    login_required,
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from models import UserORM, RoleORM, RoleUsers, tools
from app import db, app, login_manager
from models.db_models import ProjectORM


@login_manager.user_loader
def load_user(user_id):
    return UserORM.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        request_data = request.get_json()
        email = request_data["email"]
        password = request_data["password"]

        user = UserORM.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return render_template("index.html")
        else:
            flash("Invalid username or password")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/index")
@login_required
def index_home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Hash password
        hashed_pw = generate_password_hash(password, method="scrpyt")
        user_role = RoleORM.query.filter_by(name="user").first()

        # Create new user
        new_user = UserORM(username=username, password=hashed_pw, role_id=user_role.id)

        # Add user to db
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/create_role", methods=["GET", "POST"])
@login_required
def create_role():
    admin_role = RoleORM.query.filter_by(name="admin").first()
    if current_user.role_id != admin_role.id:
        flash("Only admins can create roles")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form["name"]

        new_role = RoleORM(name=name)
        db.session.add(new_role)
        db.session.commit()

        return redirect(url_for("roles"))

    return render_template("create_role.html")


@app.route("/create_user", methods=["GET", "POST"])
@login_required
def create_user():
    # Check role
    # Get form data
    # Hash password
    # Create user
    # Add to db

    return redirect(url_for("users"))


@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    user = UserORM.query.get(user_id)

    if request.method == "POST":
        # Get form data
        # Update user

        db.session.commit()
        return redirect(url_for("users"))

    return render_template("edit_user.html", user=user)


@app.route("/")
@login_required
def index():
    return render_template("reports.html")


@app.route("/projects")
@login_required
def view_projects():
    user_id = current_user.id
    projects = tools.get_projects_of_user(user_id)
    return render_template("projects.html", projects=projects)


@app.route("/project/<int:project_id>")
@login_required
def view_project(project_id):
    project = ProjectORM.query.get(project_id)
    return render_template("project.html", project=project)


@app.route("/create_project", methods=["GET", "POST"])
@login_required
def create_project():
    if request.method == "POST":
        name = request.form["name"]
        if len(name) < 3:
            flash("Name must be at least 3 chars", "error")
            return

        # Create project
        description = request.form.get("description", "")
        project = ProjectORM(
            name=name,
            description=description,
            owner_id=current_user.id,
            create_date=datetime.datetime.now(),
            update_date=datetime.datetime.now(),
        )
        db.session.add(project)
        db.session.commit()
        db.session.refresh(project)
        flash("Project created successfully!", "success")

    return redirect("/projects")


@app.route("/test")
def test():
    return render_template("test.html")


if __name__ == "__main__":
    app.run(debug=True)
