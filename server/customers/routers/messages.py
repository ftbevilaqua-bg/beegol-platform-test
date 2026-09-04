from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from server.core.database import get_session
from server.core.dependencies import get_current_user
from server.customers import repository
from server.customers.routers.customers import get_customer_or_404
from server.customers.schemas import SendMessageRequest, SendMessageResponse
from server.users.models import User

router = APIRouter(prefix="/customers/{customer_id}/message", tags=["customer-messages"])


@router.post("/send", response_model=SendMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    customer_id: int,
    payload: SendMessageRequest,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    customer = await get_customer_or_404(db, customer_id)
    return await repository.send_message(db, customer, payload.message)


@router.get("/read", response_model=list[SendMessageResponse])
async def read_messages(
    customer_id: int,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    customer = await get_customer_or_404(db, customer_id)
    return await repository.list_messages(db, customer.id)
