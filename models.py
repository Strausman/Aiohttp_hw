import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, func
import datetime

# Получение переменных окружения
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5431')

# Строка подключения
PG_DSN = (f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
          f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

# Создание асинхронного движка
engine = create_async_engine(PG_DSN, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Определение базового класса
class Base(DeclarativeBase):
    pass

# Определение модели Ads
class Ads(Base):
    __tablename__ = 'Ads'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user: Mapped[str] = mapped_column(String(120), nullable=False)
    heading: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    @property
    def dict(self):
        return {
            'id': self.id,
            'user': self.user,
            'heading': self.heading,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
        }

# Функция для создания таблиц
async def create_tables():
    async with engine.begin() as conn:
        # Создание всех таблиц
        await conn.run_sync(Base.metadata.create_all)

# Запуск создания таблиц
if __name__ == '__main__':
    asyncio.run(create_tables())