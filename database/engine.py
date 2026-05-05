from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from foundation import DATABASE_URL
from database.models import Base


engine = create_async_engine(DATABASE_URL, echo=True)

session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

bot_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
