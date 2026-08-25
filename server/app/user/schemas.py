from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.core.config import settings


def validate_beegol_email(email: str) -> str:
    domain = email.split("@")[-1].lower()
    if domain != settings.allowed_email_domain.lower():
        raise ValueError(f"Email must belong to the '{settings.allowed_email_domain}' domain")
    return email


class ProfileBase(BaseModel):
    nome: str
    email: EmailStr

    @field_validator("email")
    @classmethod
    def email_must_be_beegol(cls, value: str) -> str:
        return validate_beegol_email(value)


class ProfileCreate(ProfileBase):
    password: str


class ProfileUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    password: str | None = None

    @field_validator("email")
    @classmethod
    def email_must_be_beegol(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_beegol_email(value)


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
