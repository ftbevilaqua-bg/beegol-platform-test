from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.users.models import User
from server.customers import repository
from server.customers.routers.customers import get_customer_or_404
from server.customers.schemas import SendMessageRequest, SendMessageResponse
from server.core.database import get_db
from server.core.dependencies import get_current_user

router = APIRouter(prefix="/customers/{customer_id}/message", tags=["customer-messages"])


@router.post("/send", response_model=SendMessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    customer_id: int,
    payload: SendMessageRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    customer = get_customer_or_404(db, customer_id)
    return repository.send_message(db, customer, payload.message)


@router.get("/read", response_model=list[SendMessageResponse])
def read_messages(
    customer_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    customer = get_customer_or_404(db, customer_id)
    return repository.list_messages(db, customer.id)
