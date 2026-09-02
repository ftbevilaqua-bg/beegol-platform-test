from uvicorn import run
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.auth.router import router as auth_router
from server.profile.router import router as profile_router
from server.users.router import router as users_router
from server.customers.routers.customers import router as customer_router
from server.customers.routers.messages import router as customer_messages_router
from server.core.config import settings
from server.core.database import Base, engine

logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Beegol Platform API")

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


@app.get("/health_check", tags=["health"])
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    run("server.api:app", host="0.0.0.0", port=8000, reload=True)