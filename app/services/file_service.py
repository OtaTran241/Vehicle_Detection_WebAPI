import os
from fastapi import UploadFile
from app.core.config import settings

def save_upload_file(upload_file: UploadFile) -> str:
    """
    Save the uploaded file to the temporary directory.

    Args:
        upload_file (UploadFile): The uploaded file.

    Returns:
        str: The path to the saved file.
    """
    file_location = os.path.join(settings.TEMP_DIR, upload_file.filename)
    with open(file_location, "wb") as buffer:
        buffer.write(upload_file.file.read())
    return file_location
