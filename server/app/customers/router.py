from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.users.models import User
from app.customers import repository
from app.customers.schemas import (
    CustomerCreate,
    CustomerOut,
    CustomerUpdate,
    SendMessageRequest,
    SendMessageResponse,
)
from app.core.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/customers", tags=["customers"])


def _get_customer_or_404(db: Session, customer_id: int):
    customer = repository.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if repository.get_customer_by_phone(db, payload.phone, include_deleted=True):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this phone number already exists",
        )
    return repository.create_customer(db, payload)


@router.get("", response_model=list[CustomerOut])
def list_customers(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return repository.list_customers(db)


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return _get_customer_or_404(db, customer_id)


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    customer = _get_customer_or_404(db, customer_id)
    if payload.phone is not None:
        existing = repository.get_customer_by_phone(db, payload.phone, include_deleted=True)
        if existing and existing.id != customer.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A customer with this phone number already exists",
            )
    return repository.update_customer(db, customer, payload)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    customer = _get_customer_or_404(db, customer_id)
    repository.delete_customer(db, customer)


@router.post("/{customer_id}/send-message", response_model=SendMessageResponse)
def send_message(
    customer_id: int,
    payload: SendMessageRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    customer = _get_customer_or_404(db, customer_id)
    return repository.send_message(db, customer, payload.message)
