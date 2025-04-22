import base64
import uuid
import os
from azure.storage.blob import BlobServiceClient

_connection = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
_container = os.getenv("AZURE_CONTAINER_NAME")
_blob_service = BlobServiceClient.from_connection_string(_connection)
_container_client = _blob_service.get_container_client(_container)

def upload_file_to_blob(file_base64: str, file_name: str) -> str:
    content = base64.b64decode(file_base64)
    blob_name = f"{uuid.uuid4()}_{file_name}"
    blob_client = _container_client.get_blob_client(blob_name)
    blob_client.upload_blob(content, overwrite=True)
    account = _blob_service.account_name
    return f"https://{account}.blob.core.windows.net/{_container}/{blob_name}"
