import os
from azure.storage.blob import BlobServiceClient 
import boto3
from config import AZURE_DOC_CONTAINER, AZURE_INDEX_CONTAINER, DOC_BASE_PATH, DOC_INDEX_PATH, S3_DOC_BUCKET, S3_INDEX_BUCKET
from models.documents import Document
import config


class FileStorage:
    
    def get(self, file_id):
        raise NotImplementedError
    
    def save(self, file_path):
        raise NotImplementedError
        
class LocalStorage(FileStorage):

    def __init__(self, base_path:str):
        self.base_path = base_path

    def get(self, file_id, file_type):
        file_path = f'{self.base_path}/{file_id}.{file_type}'
        return FileReader(file_path)

    def save(self, file_id, file_type, file_path='./'):
        os.rename(file_path, f'{self.base_path}/{file_id}.{file_type}')
        
class S3Storage(FileStorage):

    def __init__(self, base_bucket):
        self.bucket = base_bucket 
        self.s3 = boto3.client('s3')

    def get(self, file_id, file_type):
        obj = self.s3.get_object(Bucket=self.bucket, Key=f'{file_id}.{file_type}')
        return FileReader(obj['Body'])

    def save(self, file_id, file_type, file_path='./'):
        self.s3.upload_file(file_path, self.bucket, f'{file_id}.{file_type}')
        
class AzureStorage(FileStorage):

    def __init__(self, container):
        self.container = container
        self.client = BlobServiceClient.from_connection_string(os.environ['AZURE_CONN_STR'])

    def get(self, file_id, file_type):
        blob = self.client.get_blob_client(self.container, f'{file_id}.{file_type}')
        stream = blob.download_blob()
        return FileReader(stream)

    def save(self, file_path, file_id, file_type):
        blob = self.client.get_blob_client(self.container, f'{file_id}.{file_type}')
        with open(file_path, 'rb') as data:
            blob.upload_blob(data)
            
class FileReader:

    def __init__(self, file_stream):
        self.file_stream = file_stream

    def __enter__(self):
        return self.file_stream

    def __exit__(self, exc_type, exc_value, traceback):
        self.file_stream.close()

def usageExample(doc_id):
    doc = Document.query.get(doc_id)
    with doc.storage.get(doc.id) as file_stream:
        # do something with file_stream
        content = file_stream.read()
        pass
    # do something with doc
    pass



# factory method for get storage instaces for doc and index, by type, and by using the different base
# path, base s3 bucket and azure container.

def get_doc_storage(storage_type='local'):
    if storage_type == 'local':
        return LocalStorage(DOC_BASE_PATH)
    elif storage_type == 's3':
        return S3Storage(S3_DOC_BUCKET)
    elif storage_type == 'azure':
        return AzureStorage(AZURE_DOC_CONTAINER)
    else:
        raise ValueError(f'Unknown storage type: {storage_type}')
    

def get_index_storage(storage_type='local'):
    if storage_type == 'local':
        return LocalStorage(DOC_INDEX_PATH)
    elif storage_type == 's3':
        return S3Storage(S3_INDEX_BUCKET)
    elif storage_type == 'azure':
        return AzureStorage(AZURE_INDEX_CONTAINER)
    else:
        raise ValueError(f'Unknown storage type: {storage_type}')

def get_doc_storage_default():
    return get_doc_storage(config.DEFAULT_DOC_STORAGE)

def get_index_storage_default():
    return get_index_storage(config.DEFAULT_INDEX_STORAGE)