from cat.mad_hatter.decorators import tool, hook, plugin
from pydantic import BaseModel
from datetime import datetime, date

class MySettings(BaseModel):
    required_int: int
    optional_int: int = 69
    required_str: str
    optional_str: str = "meow"
    required_date: date
    optional_date: date = 1679616000

@plugin
def settings_model():
    return MySettings

from typing import Iterator
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseBlobParser
from langchain.document_loaders.blob_loaders.schema import Blob
from unstructured.partition.auto import partition

class UnstructuredParser(BaseBlobParser):
    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        with blob.as_bytes_io() as file:
            doc = partition(file) # use unstructured library to parse the document
            for page,paragraph in enumerate(doc):
                content = f"{paragraph}\n"
                metadata = {'source': blob.source, 'page': page, **paragraph.metadata}
                yield Document(page_content=content, metadata=metadata)

import mimetypes

supported_extensions = [
    ".abw", ".bmp", ".csv", ".cwk", ".dbf", ".dif", ".doc", ".docm", ".docx", ".dot", ".dotm",
    ".eml", ".epub", ".et", ".eth", ".fods", ".heic", ".htm", ".html", ".hwp", ".jpeg", ".jpg",
    ".md", ".mcw", ".msg", ".mw", ".odt", ".org", ".p7s", ".pbd", ".pdf", ".png", ".pot", ".ppt",
    ".pptm", ".pptx", ".prn", ".rst", ".rtf", ".sdp", ".sxg", ".tiff", ".txt", ".tsv", ".xls",
    ".xlsx", ".xml", ".zabw"
]

mime_types = set()
for ext in supported_extensions:
    mime_type, _ = mimetypes.guess_type(f"file{ext}")
    if mime_type:
        mime_types.add(mime_type)

@hook
def rabbithole_instantiates_parsers(file_handlers: dict, cat) -> dict:
    new_handlers = {
        mime: UnstructuredParser() for mime in mime_types
    }

    file_handlers = file_handlers | new_handlers
    return file_handlers
