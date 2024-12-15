from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.background import BackgroundTasks
from starlette.responses import JSONResponse
from celery.result import AsyncResult
from app.services.file_service import save_upload_file
from celery_tasks.tasks import detect_object
from app.core.config import settings
from app.db import SessionLocal, User, DetectionResult
from app.schemas import UserCreate, UserLogin, Token
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from datetime import datetime
import base64
import os
from sqlalchemy.orm import Session
from app.core.config import settings
import asyncio
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Kiểm tra xem username đã tồn tại chưa
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Kiểm tra xem email đã tồn tại chưa
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Băm mật khẩu và tạo người dùng mới
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password, registered_at=datetime.utcnow())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully"}

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Kiểm tra xem username có tồn tại không
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Tạo access token
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

def encode_image_to_base64(image_path):
    """
    Encode an image file to a base64 string.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64 encoded string of the image.
    """
    image_file_path = os.path.join(settings.TEMP_DIR, image_path)

    with open(image_file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

@router.post("/detect")
async def detect(file: UploadFile = File(...), background_tasks: BackgroundTasks = None, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Detect objects in the uploaded image.

    Args:
        file (UploadFile): The uploaded image file.
        background_tasks (BackgroundTasks): Background tasks.
        token (str): OAuth2 token.
        db (Session): SQLAlchemy session.

    Returns:
        dict: Task ID, original image, output image, predictions.
    """
    current_user = get_current_user(token, db)
    file_location = save_upload_file(file)
    task = detect_object.delay(file_location, current_user.user_id)
    
    task_result = AsyncResult(task.id)
    while not task_result.ready():
        await asyncio.sleep(1)
    
    if task_result.state == 'SUCCESS':
        result = task_result.result

        original_image_base64 = encode_image_to_base64(result['original_image_url'])
        output_image_base64 = encode_image_to_base64(result['output_image_url'])

        return {
            "task_id": task.id,
            "original_image": original_image_base64,
            "output_image": output_image_base64,
            "predictions": result['predictions'],
            "status": task_result.state
        }
    elif task_result.state == 'FAILURE':
        return {
            "task_id": task.id,
            "status": task_result.state,
            "error": str(task_result.info)
        }
    else:
        return {
            "task_id": task.id,
            "status": task_result.state
        }

@router.get("/predictions")
def get_predictions(db: Session = Depends(get_db)):
    results = db.query(DetectionResult).all()
    return results
