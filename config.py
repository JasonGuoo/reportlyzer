# load envs from .env file
from dotenv import load_dotenv
import os, logging
from datetime import timedelta

load_dotenv()

import configparser

config = configparser.ConfigParser()
config.read("config.ini")

doc_path = config["paths"]["doc_base_path"]

paths = config["paths"]
DOC_BASE_PATH = paths.get("DOC_BASE_PATH", "NA")
S3_DOC_BUCKET = paths.get("S3_DOC_BUCKET", "NA")
AZURE_DOC_CONTAINER = paths.get("AZURE_DOC_CONTAINER", "NA")

DOC_INDEX_PATH = paths.get("DOC_INDEX_PATH", "NA")
S3_INDEX_BUCKET = paths.get("S3_INDEX_BUCKET", "NA")
AZURE_INDEX_CONTAINER = paths.get("AZURE_INDEX_CONTAINER", "NA")

DEFAULT_DOC_STORAGE = paths.get("DEFAULT_DOC_STORAGE", "NA")
DEFAULT_INDEX_STORAGE = paths.get("DEFAULT_INDEX_STORAGE", "NA")

LOGGING_LEVEL = config["logging"]["LOGGING_LEVEL"]

logging.basicConfig(level=LOGGING_LEVEL)


#: The default name of the "remember me" cookie (``remember_token``)
COOKIE_NAME = "remember_token"

#: The default time before the "remember me" cookie expires (365 days).
COOKIE_DURATION = timedelta(days=365)

#: Whether the "remember me" cookie requires Secure; defaults to ``False``
COOKIE_SECURE = False

#: Whether the "remember me" cookie uses HttpOnly or not; defaults to ``True``
COOKIE_HTTPONLY = True

#: Whether the "remember me" cookie requires same origin; defaults to ``None``
COOKIE_SAMESITE = None

#: The default flash message to display when users need to log in.
LOGIN_MESSAGE = "Please log in to access this page."

#: The default flash message category to display when users need to log in.
LOGIN_MESSAGE_CATEGORY = "message"

#: The default flash message to display when users need to reauthenticate.
REFRESH_MESSAGE = "Please reauthenticate to access this page."

#: The default flash message category to display when users need to
#: reauthenticate.
REFRESH_MESSAGE_CATEGORY = "message"

#: The default attribute to retrieve the str id of the user
ID_ATTRIBUTE = "get_id"

#: A set of session keys that are populated by Flask-Login. Use this set to
#: purge keys safely and accurately.
SESSION_KEYS = {
    "_user_id",
    "_remember",
    "_remember_seconds",
    "_id",
    "_fresh",
    "next",
}

#: A set of HTTP methods which are exempt from `login_required` and
#: `fresh_login_required`. By default, this is just ``OPTIONS``.
EXEMPT_METHODS = {"OPTIONS"}

#: If true, the page the user is attempting to access is stored in the session
#: rather than a url parameter when redirecting to the login view; defaults to
#: ``False``.
USE_SESSION_FOR_NEXT = False
