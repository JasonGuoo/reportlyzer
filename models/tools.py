import config
from models.users import User, Role, RoleUsers, LoginLedger
from models.storage import get_storage, LocalStorage
from models.documents import (
    DocumentShare,
    Document,
    ProjectDocument,
    Project,
)
import uuid, os, re, hashlib, datetime, json, logging
import requests, requests.exceptions
from urllib.parse import urlparse
from app import db
from documents import (
    DOCUMENT_PROPERTY_URL,
    DOCUMENT_PROPERTY_BASE_URL,
    DOCUMENT_PROPERTY_CHUCKSUM,
)

logger = logging.getLogger(__name__)


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
        logger.error("HTTP Error: %s", e)
        raise

    except Exception as e:
        print("Error downloading PDF:", e)
        logger.error("Error downloading PDF: %s", e)
        raise


def create_document_from_url(
    url, user_id, title=None, storage_type=config.DEFAULT_DOC_STORAGE
):
    # Download document
    try:
        doc_id = create_storage_for_url(url, storage_type)
    except Exception as e:
        logger.error("Error creating storage for url: %s", e)
        raise

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


def get_projects_of_user(user_id, sort_order="desc"):
    order = (
        Project.update_date.desc()
        if sort_order == "desc"
        else Project.update_date.asc()
    )
    projects = Project.query.filter_by(owner_id=user_id).order_by(order).all()
    return projects


def create_project(user_id, project_name):
    project = Project(name=project_name, owner_id=user_id)
    db.session.add(project)
    db.session.commit()
    return project


def change_document_title(doc_id, new_title):
    doc = Document.query.get(doc_id)

    if doc is None:
        raise ValueError(f"No document with id {doc_id}")
    doc.title = new_title
    db.session.commit()
    return doc


def share_document_with_user(doc_id, user_id):
    share = DocumentShare(document_id=doc_id, user_id=user_id)

    db.session.add(share)
    db.session.commit()

    return share


def add_documents_to_project(project_id, doc_ids):
    for doc_id in doc_ids:
        project_doc = ProjectDocument(project_id=project_id, document_id=doc_id)
        db.session.add(project_doc)

    db.session.commit()


def get_documents_in_project(project_id):
    documents = Document.query.join(
        ProjectDocument, Document.id == ProjectDocument.document_id
    ).filter(ProjectDocument.project_id == project_id)

    return documents


def update_project_update_time(project_id):
    project = Project.query.get(project_id)

    if project is None:
        raise ValueError(f"Project id {project_id} not found")

    project.update_date = datetime.datetime.now()
    db.session.commit()
    return project


def delete_project(project_id):
    project = Project.query.get(project_id)

    if project is None:
        raise ValueError(f"Project id {project_id} not found")

    project.is_deleted = True
    db.session.commit()
    return project


def add_property_to_document(doc_id, prop_name, prop_value):
    doc = Document.query.get(doc_id)

    if doc is None:
        raise ValueError(f"No document with id {doc_id}")

    # Add new property
    doc.properties[prop_name] = prop_value

    # Update update_time
    doc.update_time = datetime.now()
    db.session.commit()
    return doc


def add_tag_to_document(doc_id, tag):
    doc = Document.query.get(doc_id)
    if doc is None:
        raise ValueError(f"No document with id {doc_id}")

    # Add new tag
    doc.tags.append(tag)
    # Update update_time
    doc.update_time = datetime.now()
    db.session.commit()
    return doc


def remove_tag_from_document(doc_id, tag):
    doc = Document.query.get(doc_id)
    if doc is None:
        raise ValueError(f"No document with id {doc_id}")

    # Remove tag
    doc.tags.remove(tag)
    # Update update_time
    doc.update_time = datetime.now()
    db.session.commit()
    return doc


def get_user_documents_by_title(user_id, title_contains):
    documents = (
        Document.query.join(DocumentShare)
        .filter(
            DocumentShare.user_id == user_id, Document.title.contains(title_contains)
        )
        .all()
    )

    return documents


def get_user_documents_in_project(user_id, project_id, title_contains):
    documents = (
        Document.query.join(DocumentShare)
        .join(ProjectDocument)
        .filter(
            DocumentShare.user_id == user_id,
            ProjectDocument.project_id == project_id,
            Document.title.contains(title_contains),
        )
        .all()
    )

    return documents
