from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import router as api_router
from app.core.config import settings
from sqlalchemy import create_engine, text
import os

app = FastAPI()

# Mount the temp directory to serve static files
app.mount("/temp", StaticFiles(directory=settings.TEMP_DIR), name="temp")

app.include_router(api_router)

# Sửa đường dẫn đến thư mục static
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Thêm route để phục vụ các file tạm thời
temp_dir = settings.TEMP_DIR
# Kiểm tra và tạo thư mục nếu không tồn tại
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
app.mount("/temp", StaticFiles(directory=temp_dir), name="temp")

templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def root(request: Request):
    """
    Render the main page.

    Args:
        request (Request): FastAPI request object.

    Returns:
        TemplateResponse: Rendered main page.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login(request: Request):
    """
    Render the login page.

    Args:
        request (Request): FastAPI request object.

    Returns:
        TemplateResponse: Rendered login page.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/history")
async def history(request: Request):
    """
    Render the history page.

    Args:
        request (Request): FastAPI request object.

    Returns:
        TemplateResponse: Rendered history page.
    """
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/register")
async def register(request: Request):
    """
    Render the register page.

    Args:
        request (Request): FastAPI request object.

    Returns:
        TemplateResponse: Rendered register page.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@app.on_event("startup")
async def startup_event():
    """
    Check SQL Server connection on startup.

    Raises:
        Exception: If connection fails.
    """
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("SQLAlchemy connection successful!")
    except Exception as e:
        print(f"SQLAlchemy connection failed: {e}")
