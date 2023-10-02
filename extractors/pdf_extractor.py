# extractpdf.py

import logging
import os.path

from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import ExtractPDFOptions
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_renditions_element_type import \
    ExtractRenditionsElementType
from adobe.pdfservices.operation.pdfops.options.extractpdf.table_structure_type import TableStructureType
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation
from dotenv import load_dotenv

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

load_dotenv()

class PDFExtractor:

    def __init__(self):
        self.client_id = os.getenv('PDF_SERVICES_CLIENT_ID')
        self.client_secret = os.getenv('PDF_SERVICES_CLIENT_SECRET')

    def extract(self, pdf_file, extract_pdf_options: ExtractPDFOptions=None):
        try:
            credentials = Credentials.service_account_credentials_builder() \
                .with_client_id(self.client_id) \
                .with_client_secret(self.client_secret) \
                .build()

            execution_context = ExecutionContext.create(credentials)

            operation = ExtractPDFOperation.create_new()

            source = FileRef.create_from_local_file(pdf_file)
            operation.set_input(source)

            if extract_pdf_options is None:
                extract_pdf_options = ExtractPDFOptions.builder().with_elements_to_extract(
                    [ExtractElementType.TEXT, ExtractElementType.TABLES]) \
                    .with_elements_to_extract_renditions([ExtractRenditionsElementType.TABLES, ExtractRenditionsElementType.FIGURES])\
                    .with_table_structure_format(TableStructureType.CSV) \
                    .build()

            operation.set_options(extract_pdf_options)
            result = operation.execute(execution_context)
            return result
        except (ServiceApiException, ServiceUsageException, SdkException):
            logging.exception("Exception encountered while executing operation")

