import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from server.auth.router import router as auth_router
from server.profile.router import router as profile_router
from server.users.router import router as users_router
from server.customers.routers.customers import router as customer_router
from server.customers.routers.messages import router as customer_messages_router
from server.core.config import settings
from server.core.database import SessionLocal, engine, Base

logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(title="Beegol Platform API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(users_router)
app.include_router(customer_router)
app.include_router(customer_messages_router)


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/health")
async def health():
    async with SessionLocal() as sessao:
        await sessao.execute(text("SELECT 1"))
    return {"database": "ok"}
