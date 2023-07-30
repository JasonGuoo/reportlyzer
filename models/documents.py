from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import JSONB
from app import db, app
from .storage import FileStorage, LocalStorage, S3Storage, AzureStorage

DOCUMENT_TYPE_DOCUMENT = "document"
DOCUMENT_TYPE_INDEX = "index"
DOCUMENT_PROPERTY_URL = "url"
DOCUMENT_PROPERTY_BASE_URL = "base_url"
DOCUMENT_PROPERTY_CHUCKSUM = "checksum"
DOCUMENT_PROPERTY_CHECKSUM_TYPE = "checksum_type"


# Document Type class to store the document type info in the postgresql database
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(String(2096))
    properties = db.Column(JSONB)
    tags = db.Column(JSONB)
    create_date = db.Column(DateTime())
    type = Column(String(100))
    storage_type = db.Column(db.String(20))
    file_type = db.Column(db.String(20), default="pdf")

    @property
    def storage(self):
        if self.storage_type == "local":
            return LocalStorage()
        elif self.storage_type == "s3":
            return S3Storage()
        elif self.storage_type == "azure":
            return AzureStorage()


# Store which user has access to which document
class DocumentShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


# Each user will have several projects, in each project, there will be several documents
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    create_date = db.Column(DateTime())
    update_date = db.Column(DateTime())
    is_deleted = db.Column(Boolean, default=False)
    properties = db.Column(JSON)


class ProjectDocument(db.Model):
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), primary_key=True)
