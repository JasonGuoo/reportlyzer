import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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
from models.db_models import ProjectORM, DocumentORM, ProjectDocument, DocumentShare
import re
from urllib.parse import urlparse
from pathlib import Path


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(UserORM, user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        request_data = request.get_json()
        email = request_data["email"]
        password = request_data["password"]

        user = UserORM.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return render_template("projects.html")
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
    documents = tools.get_documents_for_project(project_id)
    return render_template("project_detail.html", project=project, documents=documents)


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


@app.route("/create_documents")
@login_required
def create_documents():
    project_id = request.args.get("project_id")
    project = ProjectORM.query.get(project_id)
    return render_template("create_documents.html", project=project)


@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    files = request.files.getlist("files")

    # Process files and save

    return {"message": "Success"}


@app.route("/add_urls/<int:project_id>", methods=["POST"])
@login_required
def add_url(project_id):
    data = request.get_json()
    urls = data["urls"]

    for url in urls:
        # Create document
        title, extension = extract_title(url)
        create_date = datetime.datetime.now()
        prop = {'url': url}
        doc = DocumentORM(title=title, properties=prop, tags={},
                          create_date=create_date, file_type=extension)

        db.session.add(doc)
        db.session.commit()
        db.session.refresh(doc)

        # Get project
        # project_id = data["project_id"]
        # project = ProjectORM.query.get(project_id)

        # Link document to project
        project_doc = ProjectDocument(project_id=project_id, document_id=doc.id)

        # Link the document to DocumentShare
        doc_share = DocumentShare(document_id=doc.id, user_id=current_user.id)

        db.session.add(project_doc)
        db.session.add(doc_share)
        db.session.commit()
        db.session.refresh(doc)
        db.session.refresh(project_doc)
        db.session.refresh(doc_share)

    # return http 200 and message
    return jsonify({"message": "URLs added successfully"}), 200

@app.route("/build_index/<int:project_id>", methods=["POST"])
@login_required
def build_index(project_id):

    return jsonify({"message": "Index built successfully"}),  200
def extract_title(url):
    try:
        # Get domain name without www
        domain = urlparse(url).netloc.split('www.')[-1]

        # Remove protocol and get page path
        page = url.split(domain)[1]
        page = re.sub(r'^:/?', '', page)

        # Remove everything after / in page path
        page = page.split('/')[-1]

        # Remove any query parameters
        page = page.split('?')[0]

        # Replace hyphens with spaces
        page = page.replace('-', '_')

        # Capitalize words and return
        title = page.title()
        # Get filename from URL path
        filename = Path(urlparse(url).path).name

        # Get extension
        ext = Path(filename).suffix

        return title, ext

    except:
        return None


@app.route("/test")
def test():
    return render_template("test.html")


if __name__ == "__main__":
    app.run(debug=True)
