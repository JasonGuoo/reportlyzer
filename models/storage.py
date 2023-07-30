import hashlib
import os
from azure.storage.blob import BlobServiceClient
import boto3
from botocore.exceptions import ClientError

from config import (
    AZURE_DOC_CONTAINER,
    AZURE_INDEX_CONTAINER,
    DOC_BASE_PATH,
    DOC_INDEX_PATH,
    S3_DOC_BUCKET,
    S3_INDEX_BUCKET,
)
from models.documents import Document
import config
from models.tools import get_file_checksum


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
