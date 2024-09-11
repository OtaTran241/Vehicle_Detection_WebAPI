from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    """
    Base model for user.

    Attributes:
        username (str): Username.
        email (str): Email address.
    """
    username: str
    email: str

class UserCreate(UserBase):
    """
    Model for creating a user.

    Attributes:
        password (str): User password.
    """
    password: str

class UserLogin(BaseModel):
    """
    Model for user login.

    Attributes:
        username (str): Username.
        password (str): User password.
    """
    username: str
    password: str

class DetectionResultBase(BaseModel):
    """
    Base model for detection result.

    Attributes:
        task_id (str): Task ID.
        original_image_path (str): Path to the original image.
        processed_image_path (str): Path to the processed image.
        status (str): Status of the detection.
        predicted_at (datetime): Prediction date.
        user_id (int): User ID.
    """
    task_id: str
    original_image_path: str
    processed_image_path: str
    status: str
    predicted_at: datetime
    user_id: int

class DetectionResultCreate(DetectionResultBase):
    """
    Model for creating a detection result.
    """
    pass

class DetectionResult(DetectionResultBase):
    """
    Model for detection result.

    Attributes:
        result_id (int): Result ID.
    """
    result_id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    """
    Model for token.

    Attributes:
        access_token (str): Access token.
        token_type (str): Token type.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Model for token data.

    Attributes:
        username (str | None): Username.
    """
    username: str | None = None
