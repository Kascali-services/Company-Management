import os
import logging
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.core.database import Base, engine
from app.routes import unternehmen_routes, person_routes, export_routes
from app.utils.constants import BUNDESLAENDER

# Configure logging for the application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Only create tables if not in test mode
if os.getenv("DATABASE_URL", "").startswith("postgresql"):
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="Unternehmen Management System")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(unternehmen_routes.router)
app.include_router(person_routes.router)
app.include_router(export_routes.router)

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "bundeslaender": BUNDESLAENDER})
