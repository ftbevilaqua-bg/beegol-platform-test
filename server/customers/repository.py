from datetime import datetime, timezone

from sqlalchemy.orm import Session

from server.customers.models import Customer, CustomerMessage
from server.customers.schemas import CustomerCreate, CustomerUpdate


def list_customers(db: Session) -> list[Customer]:
    return db.query(Customer).filter(Customer.deleted_at.is_(None)).order_by(Customer.id).all()


def get_customer(db: Session, customer_id: int) -> Customer | None:
    return db.query(Customer).filter(Customer.id == customer_id, Customer.deleted_at.is_(None)).first()


def get_customer_by_phone(db: Session, phone: str, *, include_deleted: bool = False) -> Customer | None:
    query = db.query(Customer).filter(Customer.phone == phone)
    if not include_deleted:
        query = query.filter(Customer.deleted_at.is_(None))
    return query.first()


def create_customer(db: Session, payload: CustomerCreate) -> Customer:
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(db: Session, customer: Customer, updates: CustomerUpdate) -> Customer:
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer: Customer) -> None:
    customer.deleted_at = datetime.now(timezone.utc)
    db.commit()


def send_message(db: Session, customer: Customer, message: str) -> CustomerMessage:
    record = CustomerMessage(customer_id=customer.id, message=message)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_messages(db: Session, customer_id: int) -> list[CustomerMessage]:
    return (
        db.query(CustomerMessage)
        .filter(CustomerMessage.customer_id == customer_id, CustomerMessage.deleted_at.is_(None))
        .order_by(CustomerMessage.sent_at)
        .all()
    )


def delete_message(db: Session, message: CustomerMessage) -> None:
    message.deleted_at = datetime.now(timezone.utc)
    db.commit()
