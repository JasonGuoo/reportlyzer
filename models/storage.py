import os
from azure.storage.blob import BlobServiceClient 
import boto3
from models.documents import Document

class FileStorage:
    
    def get(self, file_id):
        raise NotImplementedError
    
    def save(self, file_path):
        raise NotImplementedError
        
class LocalStorage(FileStorage):

    def __init__(self):
        self.base_path = os.environ['FILE_BASE_PATH']

    def get(self, file_id, file_type):
        file_path = f'{self.base_path}/{file_id}.{file_type}'
        return FileReader(file_path)

    def save(self, file_id, file_type, file_path='./'):
        os.rename(file_path, f'{self.base_path}/{file_id}.{file_type}')
        
class S3Storage(FileStorage):

    def __init__(self):
        self.bucket = os.environ['S3_BUCKET'] 
        self.s3 = boto3.client('s3')

    def get(self, file_id, file_type):
        obj = self.s3.get_object(Bucket=self.bucket, Key=f'{file_id}.{file_type}')
        return FileReader(obj['Body'])

    def save(self, file_id, file_type, file_path='./'):
        self.s3.upload_file(file_path, self.bucket, f'{file_id}.{file_type}')
        
class AzureStorage(FileStorage):

    def __init__(self):
        self.container = os.environ['AZURE_CONTAINER']
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