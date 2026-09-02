from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    active: bool = True

    name: str
    phone: str
    address: str

    conversation_id: str | None = None
    status: str = "open"


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    active: bool | None = None

    name: str | None = None
    phone: str | None = None
    address: str | None = None

    conversation_id: str | None = None
    status: str | None = None


class CustomerOut(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class SendMessageRequest(BaseModel):
    message: str


class SendMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    message: str
    sent_at: datetime
