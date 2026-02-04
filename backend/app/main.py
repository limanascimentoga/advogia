from fastapi import FastAPI
from app.config import APP_NAME
from app.database import Base, engine
from app.routers import health, auth
from app.routers import documents

app = FastAPI(title=APP_NAME)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
