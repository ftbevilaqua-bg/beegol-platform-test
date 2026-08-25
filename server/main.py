import logging

from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.user.profile_router import router as profile_router
from app.user.users_router import router as users_router
from app.user import models as user_models  # noqa: F401 (register SQLAlchemy models)
from app.customer.router import router as customer_router
from app.customer import models as customer_models  # noqa: F401 (register SQLAlchemy models)
from app.core.database import Base, engine

logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Beegol Platform API")

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(users_router)
app.include_router(customer_router)


@app.get("/health_check", tags=["health"])
def health_check():
    return {"status": "ok"}
