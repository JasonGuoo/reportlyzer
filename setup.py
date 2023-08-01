import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import (
    User,
    Role,
    RoleUsers,
    LoginLedger,
    Document,
    Project,
    DocumentShare,
    ProjectDocument,
    Index,
)


def dropall():
    db.drop_all()


def setup():
    # create the database
    db.metadata.create_all(
        bind=db.engine,
        tables=[
            User.__table__,
            Role.__table__,
            RoleUsers.__table__,
            LoginLedger.__table__,
        ],
    )
    # create admin role
    admin_role = Role(
        role_name="admin",
        role_description="admin role",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # create user role
    user_role = Role(
        role_name="user",
        role_description="user role",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # create admin user
    admin_user = User(
        username="admin",
        password=generate_password_hash("admin", method="scrypt"),
        # password='password',
        name="admin",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        email="jingyuanguo@hotmail.com",
    )

    # create user user
    user_user = User(
        username="user",
        password=generate_password_hash("user", method="scrypt"),
        # password='password',
        name="user",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        email="user@user.com",
    )

    # write all to the database
    db.session.add(admin_role)
    db.session.add(user_role)
    db.session.add(admin_user)
    db.session.add(user_user)
    db.session.commit()
    db.session.refresh(admin_role)
    db.session.refresh(user_role)
    db.session.refresh(admin_user)
    db.session.refresh(user_user)

    # create role user item
    admin_role_user = RoleUsers(
        role_id=admin_role.id,
        user_id=admin_user.id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    user_role_user = RoleUsers(
        role_id=user_role.id,
        user_id=user_user.id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    db.session.add(admin_role_user)
    db.session.add(user_role_user)

    db.session.commit()
    db.session.refresh(admin_role_user)
    db.session.refresh(user_role_user)

    db.metadata.create_all(
        bind=db.engine, tables=[Document.__table__, Project.__table__]
    )
    db.metadata.create_all(
        bind=db.engine, tables=[DocumentShare.__table__, ProjectDocument.__table__]
    )

    print("Database initialized!")


with app.app_context():
    dropall()
    setup()
