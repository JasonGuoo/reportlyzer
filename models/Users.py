# create User class, store the user info in the postgresql database
# 
# Path: modules/Users.py
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .App import db, app, login_manager

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    password = Column(String(1000))
    name = Column(String(100))
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    is_active = Column(Boolean(), default=True)
    email = Column(String(100), unique=True)

    # add email as a parameter
    def __init__(self, username, password, name, created_at, updated_at, email):
        self.username = username
        self.password = password
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at
        self.email = email

    def __repr__(self):
        return "<User {}>".format(self.username)

    

# Role class to store the role info in the postgresql database
# The role class should have role id, role name, role description, 
# created at, updated at
class Role(db.Model, UserMixin):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    role_name = Column(String(100), unique=True)
    role_description = Column(String(100))
    created_at = Column(DateTime())
    updated_at = Column(DateTime())

    def __init__(self, role_name, role_description, created_at, updated_at):
        self.role_name = role_name
        self.role_description = role_description
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return "<Role {}>".format(self.role_name)


# create a RoleUsers class to store the role and user relationship
# in the postgresql database
class RoleUsers(db.Model, UserMixin):
    __tablename__ = "role_users"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    role_id = Column(Integer)
    created_at = Column(DateTime())
    updated_at = Column(DateTime())

    def __init__(self, user_id, role_id, created_at, updated_at):
        self.user_id = user_id
        self.role_id = role_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return "<RoleUsers {}>".format(self.user_id)

class LoginLedger(db.Model, UserMixin):
    __tablename__ = "login_ledger"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    login_time = Column(DateTime())
    logout_time = Column(DateTime())
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    ip_address = Column(String(100))

    def __init__(self, user_id, login_time, logout_time, created_at, updated_at, ip_address):
        self.user_id = user_id
        self.login_time = login_time
        self.logout_time = logout_time
        self.created_at = created_at
        self.updated_at = updated_at
        self.ip_address = ip_address

    def __repr__(self):
        return "<LoginLedger {}>".format(self.user_id)