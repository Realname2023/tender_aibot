from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Tender


async def add_user(
        session: AsyncSession,
        user_id: int,
        full_name: str | None = None,
        user_name: str | None = None,
):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(user_id=user_id, full_name=full_name, user_name=user_name)
        )
        await session.commit()


async def add_tender(
        session: AsyncSession,
        user_id: int,
        number: str,
        url: str
) -> Tender | None:
    # Проверяем нет ли уже такого тендера у этого пользователя
    query = select(Tender).where(
        Tender.user_id == user_id,
        Tender.number == number
    )
    result = await session.execute(query)
    existing = result.scalar_one_or_none()

    if existing is not None:
        return None  # уже существует

    tender = Tender(user_id=user_id, number=number, url=url)
    session.add(tender)
    await session.commit()
    await session.refresh(tender)  # обновляем объект после commit чтобы получить id и другие поля
    return tender


async def delete_users_tenders(session: AsyncSession, user_id: int):
    query = delete(Tender).where(Tender.user_id == user_id)
    await session.execute(query)
    await session.commit()
