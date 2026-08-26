from datetime import datetime
from sqlalchemy import BigInteger, String, Float, Boolean, DateTime, Text, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    language: Mapped[str] = mapped_column(String(5), default="bn")

    # Quotex data from postback
    trader_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    country: Mapped[str | None] = mapped_column(String(10), nullable=True)
    total_deposit: Mapped[float] = mapped_column(Float, default=0.0)
    total_withdraw: Mapped[float] = mapped_column(Float, default=0.0)
    last_deposit: Mapped[float] = mapped_column(Float, default=0.0)
    last_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Invite link management
    invite_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    invite_link_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    has_joined: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PostbackLog(Base):
    __tablename__ = "postback_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    click_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    trader_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    event_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sumdep: Mapped[float] = mapped_column(Float, default=0.0)
    sumwithdraw: Mapped[float] = mapped_column(Float, default=0.0)
    country: Mapped[str | None] = mapped_column(String(10), nullable=True)
    raw_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
