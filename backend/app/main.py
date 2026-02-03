from fastapi import FastAPI
from app.config import APP_NAME
from app.database import Base, engine
from app.routers import health, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title=APP_NAME)

app.include_router(health.router)
app.include_router(auth.router)
