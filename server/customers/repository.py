from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.customers.models import Customer, CustomerMessage
from server.customers.schemas import CustomerCreate, CustomerUpdate


async def list_customers(db: AsyncSession) -> list[Customer]:
    result = await db.execute(
        select(Customer).where(Customer.deleted_at.is_(None)).order_by(Customer.id)
    )
    return list(result.scalars().all())


async def get_customer(db: AsyncSession, customer_id: int) -> Customer | None:
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id, Customer.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def get_customer_by_phone(
    db: AsyncSession, phone: str, *, include_deleted: bool = False
) -> Customer | None:
    query = select(Customer).where(Customer.phone == phone)
    if not include_deleted:
        query = query.where(Customer.deleted_at.is_(None))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_customer(db: AsyncSession, payload: CustomerCreate) -> Customer:
    customer = Customer(**payload.model_dump())
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


async def update_customer(
    db: AsyncSession, customer: Customer, updates: CustomerUpdate
) -> Customer:
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    await db.commit()
    await db.refresh(customer)
    return customer


async def delete_customer(db: AsyncSession, customer: Customer) -> None:
    customer.deleted_at = datetime.now(UTC)
    await db.commit()


async def send_message(db: AsyncSession, customer: Customer, message: str) -> CustomerMessage:
    record = CustomerMessage(customer_id=customer.id, message=message)
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def list_messages(db: AsyncSession, customer_id: int) -> list[CustomerMessage]:
    result = await db.execute(
        select(CustomerMessage)
        .where(CustomerMessage.customer_id == customer_id, CustomerMessage.deleted_at.is_(None))
        .order_by(CustomerMessage.sent_at)
    )
    return list(result.scalars().all())


async def delete_message(db: AsyncSession, message: CustomerMessage) -> None:
    message.deleted_at = datetime.now(UTC)
    await db.commit()
