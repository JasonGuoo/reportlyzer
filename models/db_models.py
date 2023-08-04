# create User class, store the user info in the postgresql database
#
# Path: modules/Users.py
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app import db, app, login_manager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import JSONB
from app import db, app
import hashlib, os
from azure.storage.blob import BlobServiceClient
from config import (
    AZURE_DOC_CONTAINER,
    AZURE_INDEX_CONTAINER,
    DOC_BASE_PATH,
    DOC_INDEX_PATH,
    S3_DOC_BUCKET,
    S3_INDEX_BUCKET,
)
import config
import boto3, datetime
from botocore.exceptions import ClientError


class UserORM(db.Model, UserMixin):
    __tablename__ = "user"
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
class RoleORM(db.Model, UserMixin):
    __tablename__ = "role"
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
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    login_time = Column(DateTime())
    logout_time = Column(DateTime())
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    ip_address = Column(String(100))

    def __init__(
        self, user_id, login_time, logout_time, created_at, updated_at, ip_address
    ):
        self.user_id = user_id
        self.login_time = login_time
        self.logout_time = logout_time
        self.created_at = created_at
        self.updated_at = updated_at
        self.ip_address = ip_address

    def __repr__(self):
        return "<LoginLedger {}>".format(self.user_id)


DOCUMENT_TYPE_DOCUMENT = "document"
DOCUMENT_TYPE_INDEX = "index"
DOCUMENT_PROPERTY_URL = "url"
DOCUMENT_PROPERTY_BASE_URL = "base_url"
DOCUMENT_PROPERTY_CHUCKSUM = "checksum"
DOCUMENT_PROPERTY_CHECKSUM_TYPE = "checksum_type"

INDEX_TYPE_PDF = "INDEX_TYPE_PDF"
INDEX_TYPE_IMAGE = "INDEX_TYPE_IMAGE"
INDEX_TYPE_WEBPAGE = "INDEX_TYPE_WEBPAGE"
INDEX_STATUS_NOT_INDEXED = "Not Indexed"
INDEX_STATUS_INDEXING = "Indexing"
INDEX_STATUS_INDEXED = "Indexed"


# Document Type class to store the document type info in the postgresql database
class DocumentORM(db.Model):
    __tablename__ = "document"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(String(2096))
    properties = db.Column(JSONB)
    tags = db.Column(JSONB)
    create_date = db.Column(DateTime())
    type = Column(String(100))
    storage_type = db.Column(db.String(20), default="local")
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
    document_id = db.Column(
        db.Integer, db.ForeignKey("document.id")
    )  # the table name would be lower case, so the User model map to "user" table
    update_time = db.Column(db.DateTime(), default=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


# Each user will have several projects, in each project, there will be several documents
class ProjectORM(db.Model):
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    description = db.Column(db.String)

    create_date = db.Column(DateTime())
    update_date = db.Column(DateTime())
    is_deleted = db.Column(Boolean, default=False)
    properties = db.Column(JSON)


class ProjectDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"))


class IndexORM(db.Model):
    __tablename__ = "index"
    index_id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"))

    storage_type = db.Column(db.String, default=config.DEFAULT_INDEX_STORAGE)
    index_type = db.Column(db.String, default=INDEX_TYPE_PDF)
    index_extract_file_path = db.Column(db.String)
    index_file_path = db.Column(db.String)
    index_status = db.Column(db.String(30), default=INDEX_STATUS_NOT_INDEXED)
    index_date = db.Column(DateTime(), default=None)
    index_properties = db.Column(JSONB)

    # embedding method and llm_model, default is using chatgpt-3.5
    embedding_method = db.Column(db.String, default="text-embedding-ada-002")
    embedding_model = db.Column(db.String, default="gpt-3.5-turbo-0613")
    embedding_model_version = db.Column(db.String, default="2023-06-13")

    def build(self):
        # Index building logic:
        # - Read document contents from self.document
        # - Calculate embeddings using self.embedding_method
        # - Query LLM using self.llm_model
        # - Write to storage: self.storage
        pass


class Storage:
    def __init__(
        self, file_id, file_type, file_ext, base_path=None, storage_type="local"
    ):
        self.file_id = file_id
        self.file_ext = file_ext
        self.file_type = file_type
        self.storage_type = storage_type
        self.checksum = None

        if file_type == "document":
            if self.storage_type == "local":
                self.base_path = config.DOC_BASE_PATH
            elif self.storage_type == "s3":
                self.base_path = config.S3_DOC_BUCKET
            elif self.storage_type == "azure":
                self.base_path = config.AZURE_DOC_CONTAINER

        elif file_type == "index":
            if self.storage_type == "local":
                self.base_path = config.INDEX_BASE_PATH
            elif self.storage_type == "s3":
                self.base_path = config.S3_INDEX_BUCKET
            elif self.storage_type == "azure":
                self.base_path = config.AZURE_INDEX_CONTAINER

    def read(self):
        raise NotImplementedError

    def write(self, data):
        raise NotImplementedError

    def get_checksum(self):
        raise NotImplementedError


class LocalStorage(Storage):
    def read(self):
        try:
            path = f"{self.base_path}/{self.file_id}.{self.file_ext}"
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Local file not found at {path}")
        except Exception as e:
            print("Error reading local file:", e)

    def write(self, data):
        try:
            path = f"{self.base_path}/{self.file_id}.{self.file_ext}"
            with open(path, "wb") as f:
                f.write(data)
        except Exception as e:
            print("Error writing local file:", e)

    def get_checksum(self):
        if self.checksum is None:
            path = f"{self.base_path}/{self.file_id}.{self.file_ext}"
            self.checksum = get_file_checksum(path)
        return self.checksum


class S3Storage(Storage):
    def __init__(self, file_id, file_type, file_ext):
        super().__init__(file_id, file_type, file_ext)
        self.s3 = boto3.client("s3")

        # Use base_path from parent class as bucket name
        self.bucket = self.base_path

    def read(self):
        try:
            obj = self.s3.get_object(
                Bucket=self.bucket, Key=f"{self.file_id}.{self.file_ext}"
            )
            return obj["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                print("Object does not exist")
            else:
                print("Error getting object:", e)
        except Exception as e:
            print("Error reading from S3:", e)

    def write(self, data):
        try:
            self.s3.put_object(
                Body=data, Bucket=self.bucket, Key=f"{self.file_id}.{self.file_ext}"
            )
        except ClientError as e:
            print("Error writing to S3:", e)
        except Exception as e:
            print("Error writing to S3:", e)

    def get_checksum(self):
        if self.checksum is None:
            obj = self.s3.get_object(
                Bucket=self.bucket, Key=f"{self.file_id}.{self.file_ext}"
            )
            data = obj["Body"].read()
            self.checksum = hashlib.sha256(data).hexdigest()
        return self.checksum


class AzureStorage(Storage):
    def __init__(self, file_id, file_type, file_ext):
        super().__init__(file_id, file_type, file_ext)
        self.container = self.base_path
        self.conn_str = config.AZURE_CONN_STR

    def read(self):
        try:
            blob = self.client.get_blob_client(
                self.container, f"{self.file_id}.{self.file_ext}"
            )
            return blob.download_blob().readall()
        except Exception as e:
            print("Error reading Azure blob:", e)

    def write(self, data):
        try:
            blob = self.client.get_blob_client(
                self.container, f"{self.file_id}.{self.file_ext}"
            )
            blob.upload_blob(data)
        except Exception as e:
            print("Error writing Azure blob:", e)

    def get_checksum(self):
        if self.checksum is None:
            blob = self.client.get_blob_client(
                self.container, f"{self.file_id}.{self.file_ext}"
            )
            data = blob.download_blob()
            self.checksum = hashlib.sha256(data.readall()).hexdigest()
        return self.checksum


# factory method for get storage instaces for doc and index, by type, and by using the different base
# path, base s3 bucket and azure container.


def get_storage(file_id, file_type, file_ext, base_path=None, storage_type="local"):
    if storage_type == "local":
        return LocalStorage(file_id, file_type, file_ext, base_path=None)
    elif storage_type == "s3":
        return S3Storage(
            file_id,
            file_type,
            file_ext,
            base_path=None,
        )
    elif storage_type == "azure":
        return AzureStorage(
            file_id,
            file_type,
            file_ext,
            base_path=None,
        )
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")


def get_file_checksum(file_path):
    # Open file in binary mode
    with open(file_path, "rb") as f:
        # Read contents of the file
        data = f.read()

        # Return SHA256 hash
        return hashlib.sha256(data).hexdigest()


# example code:
# local_storage = LocalStorage('file1', 'document', 'txt')

# # Read
# data = local_storage.read()

# # Write
# local_storage.write(b'Hello World!')

# s3_storage = S3Storage('file2', 'index', 'json')

# # Read
# data = s3_storage.read()

# # Write
# s3_storage.write(b'{"name": "John"}')

# azure_storage = AzureStorage('file3', 'document', 'pdf')

# # Read
# data = azure_storage.read()

# # Write
# with open('report.pdf', 'rb') as f:
#   azure_storage.write(f.read())
