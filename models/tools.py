import config
from models.users import User, Role, RoleUsers, LoginLedger
from models.storage import get_storage, LocalStorage
from models.documents import (
    DocumentShare,
    Document,
    DocumentTag,
    ProjectDocument,
    Project,
)
import uuid, os, re, hashlib
import requests, requests.exceptions
from urllib.parse import urlparse
from app import db
from documents import (
    DOCUMENT_PROPERTY_URL,
    DOCUMENT_PROPERTY_BASE_URL,
    DOCUMENT_PROPERTY_CHUCKSUM,
)
import datetime
import json


def generate_doc_id() -> str:
    return str(uuid.uuid4())


# Get filename from url
def create_storage_for_url(url, storage_type=config.DEFAULT_DOC_STORAGE) -> str:
    try:
        # Generate random doc id
        doc_id = generate_doc_id()

        if url.endswith(".pdf"):
            # Download PDF from url
            response = requests.get(url)
            response.raise_for_status()

            # Save to storage
            storage = get_storage(
                file_id=doc_id,
                file_type="document",
                file_ext="pdf",
                storage_type=storage_type,
            )
            storage.write(response.content)

        return doc_id

    except requests.HTTPError as e:
        print("HTTP Error:", e)
        raise

    except Exception as e:
        print("Error downloading PDF:", e)
        raise


def create_document_from_url(
    url, user_id, title=None, storage_type=config.DEFAULT_DOC_STORAGE
):
    # Download document
    doc_id = create_storage_for_url(url, storage_type)

    if title is None:
        title = get_filename_from_url(url)

    # Create Document record
    doc = Document(id=doc_id, title=title, user_id=user_id)

    # Add timestamp
    doc.create_date = datetime.datetime.now()

    # Get checksum
    storage = get_storage(doc_id, "document", "pdf", storage_type)
    checksum = storage.checksum

    # Build properties
    doc.properties = json.dumps(
        {
            DOCUMENT_PROPERTY_URL: url,
            DOCUMENT_PROPERTY_BASE_URL: urlparse(url).netloc,
            DOCUMENT_PROPERTY_CHUCKSUM: checksum,
        }
    )

    db.session.add(doc)

    # Create share association
    share = DocumentShare(document_id=doc_id, user_id=user_id)
    db.session.add(share)

    db.session.commit()

    return doc_id


def get_filename_from_url(url):
    parsed = urlparse(url)
    filename = parsed.path.split("/")[-1]

    # Remove query params
    filename = re.sub(r"\?.+$", "", filename)

    # Remove special chars
    filename = re.sub(r"[^\w\s-]", "", filename)

    # Replace spaces with underscores
    filename = filename.replace(" ", "_")

    return filename


def get_file_checksum(file_path):
    # Open file in binary mode
    with open(file_path, "rb") as f:
        # Read contents of the file
        data = f.read()

        # Return SHA256 hash
        return hashlib.sha256(data).hexdigest()
