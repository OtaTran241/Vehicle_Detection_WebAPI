import logging
from celery import Celery
from detection.detection_model import run_detection
from app.core.config import settings
from app.db import SessionLocal, DetectionResult
from sqlalchemy.orm import Session
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery('celery_tasks',
                    broker=settings.CELERY_BROKER_URL,
                    backend=settings.CELERY_RESULT_BACKEND)

def get_db():
    """
    Get a database session.

    Yields:
        Session: SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@celery_app.task(bind=True)
def detect_object(self, file_path, user_id):
    """
    Celery task to run vehicle detection on an image file.

    Args:
        file_path (str): The path to the input image file.
        user_id (int): The ID of the user who initiated the task.

    Returns:
        dict: A dictionary containing the output image path and a success message.
    """
    db: Session = next(get_db())
    try:
        logger.info(f"Starting detection for file: {file_path}")
        result = run_detection(file_path)
        result['task_id'] = self.request.id
        logger.info(f"Detection completed: {result}")

        # Debug prints
        print(f"Original Image Path: {result['original_image_url']}")
        print(f"Processed Image Path: {result['output_image_url']}")

        detection_result = DetectionResult(
            task_id=self.request.id,
            original_image_path=result['original_image_url'],
            processed_image_path=result['output_image_url'],
            status='SUCCESS',
            predicted_at=datetime.utcnow(),
            user_id=user_id
        )
        db.add(detection_result)
        db.commit()
        db.refresh(detection_result)

        return result
    except Exception as e:
        logger.error(f"Error during detection: {str(e)}")
        detection_result = db.query(DetectionResult).filter(DetectionResult.task_id == self.request.id).first()
        if detection_result:
            detection_result.status = 'FAILURE'
            db.commit()
            db.refresh(detection_result)
        raise