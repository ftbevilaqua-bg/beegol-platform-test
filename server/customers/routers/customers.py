from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from server.core.database import get_session
from server.core.dependencies import get_current_user
from server.customers import repository
from server.customers.schemas import CustomerCreate, CustomerOut, CustomerUpdate
from server.users.models import User

router = APIRouter(prefix="/customers", tags=["customers"])


async def get_customer_or_404(db: AsyncSession, customer_id: int):
    customer = await repository.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    if await repository.get_customer_by_phone(db, payload.phone, include_deleted=True):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this phone number already exists",
        )
    return await repository.create_customer(db, payload)


@router.get("", response_model=list[CustomerOut])
async def list_customers(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    return await repository.list_customers(db)


@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    return await get_customer_or_404(db, customer_id)


@router.put("/{customer_id}", response_model=CustomerOut)
async def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    customer = await get_customer_or_404(db, customer_id)
    if payload.phone is not None:
        existing = await repository.get_customer_by_phone(db, payload.phone, include_deleted=True)
        if existing and existing.id != customer.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A customer with this phone number already exists",
            )
    return await repository.update_customer(db, customer, payload)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    customer = await get_customer_or_404(db, customer_id)
    await repository.delete_customer(db, customer)
