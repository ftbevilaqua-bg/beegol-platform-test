from sqlalchemy.orm import Session

from app.customer.models import Customer, CustomerMessage
from app.customer.schemas import CustomerCreate, CustomerUpdate


def list_customers(db: Session) -> list[Customer]:
    return db.query(Customer).order_by(Customer.id).all()


def get_customer(db: Session, customer_id: int) -> Customer | None:
    return db.query(Customer).filter(Customer.id == customer_id).first()


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
    db.delete(customer)
    db.commit()


def send_message(db: Session, customer: Customer, message: str) -> CustomerMessage:
    record = CustomerMessage(customer_id=customer.id, message=message)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
