from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """
    User model.

    Attributes:
        user_id (int): Primary key.
        username (str): Username.
        email (str): Email address.
        password (str): Hashed password.
        registered_at (datetime): Registration date.
        results (relationship): Relationship to DetectionResult.
    """
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    registered_at = Column(DateTime)
    
    results = relationship("DetectionResult", back_populates="user")

class DetectionResult(Base):
    """
    DetectionResult model.

    Attributes:
        result_id (int): Primary key.
        task_id (str): Task ID.
        original_image_path (str): Path to the original image.
        processed_image_path (str): Path to the processed image.
        status (str): Status of the detection.
        predicted_at (datetime): Prediction date.
        user_id (int): Foreign key to User.
        user (relationship): Relationship to User.
    """
    __tablename__ = "results"

    result_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    original_image_path = Column(String)
    processed_image_path = Column(String)
    status = Column(String)
    predicted_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship("User", back_populates="results")


