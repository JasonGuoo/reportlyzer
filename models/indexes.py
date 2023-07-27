import os
from storage import FileStorage, LocalStorage, S3Storage, AzureStorage , FileReader, get_doc_storage, get_index_storage
from app import app, db
import config

class Index(db.Model):

  document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
  document = db.relationship('Document', backref='indexes')

  storage_type = db.Column(db.String, default=config.DEFAULT_INDEX_STORAGE)
  
  @property
  def storage(self):
    return get_doc_storage(self.storage_type)

  embedding_method = db.Column(db.String, default='tfidf')

  llm_model = db.Column(db.String, default='llama')

  def build(self):
    # Index building logic:
    # - Read document contents from self.document 
    # - Calculate embeddings using self.embedding_method
    # - Query LLM using self.llm_model
    # - Write to storage: self.storage
    pass