from sqlalchemy import DateTime, ForeignKey, String, Text, BigInteger, Boolean, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    user_name: Mapped[str] = mapped_column(String(150), nullable=True)
    full_name: Mapped[str] = mapped_column(String(500), nullable=True)

    def __str__(self):
        return self.full_name


class Tender(Base):
    __tablename__ = 'tenders'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    number: Mapped[str] = mapped_column(String(150), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)

    user: Mapped['User'] = relationship(backref='tenders', lazy="selectin")

    def __str__(self):
        return self.number
