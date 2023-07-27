import os
from storage import FileStorage, LocalStorage, S3Storage, AzureStorage 
from app import app, db

class Index(db.Model):

  document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
  document = db.relationship('Document', backref='indexes')

  storage_type = db.Column(db.String, default=os.getenv('DEFAULT_INDEX_STORAGE', 'local'))
  
  @property
  def storage(self):
    if self.storage_type == 'local':
      return LocalStorage()
    elif self.storage_type == 's3':
      return S3Storage()
    elif self.storage_type == 'azure':
      return AzureStorage()

  embedding_method = db.Column(db.String, default='tfidf')

  llm_model = db.Column(db.String, default='llama')

  def build(self):
    # Index building logic:
    # - Read document contents from self.document 
    # - Calculate embeddings using self.embedding_method
    # - Query LLM using self.llm_model
    # - Write to storage: self.storage
    pass