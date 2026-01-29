from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, JSON, Integer
from typing import Optional
from datetime import datetime
import json
import logging
from pathlib import Path

from src.config import config
from src.s3_storage import s3_storage  # Импортируем S3 хранилище

logger = logging.getLogger(__name__)

# Используем локальный SQLite файл
engine = create_async_engine(config.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Cocktail(Base):
    __tablename__ = "cocktails"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ingredients: Mapped[dict] = mapped_column(JSON, nullable=False)
    recipe: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    strength: Mapped[int] = mapped_column(Integer, default=0)
    difficulty: Mapped[str] = mapped_column(String(20), default="легко")
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    def get_ingredients_text(self):
        return "\n".join([f"• {item}: {amount}" for item, amount in self.ingredients.items()])
    
    def get_tags_text(self):
        return ", ".join(f"#{tag}" for tag in self.tags) if self.tags else "нет тегов"

class Database:
    @staticmethod
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    @staticmethod
    async def get_session() -> AsyncSession:
        async with async_session() as session:
            yield session
    
    @staticmethod
    @staticmethod
    async def add_cocktail(name, description, ingredients, recipe, tags, strength, difficulty, image_url=None):
        async with async_session() as session:
            cocktail = Cocktail(
                name=name,
                description=description,
                ingredients=ingredients,
                recipe=recipe,
                tags=tags,
                strength=strength,
                difficulty=difficulty,
                image_url=image_url
            )
            session.add(cocktail)
            await session.commit()
            await session.refresh(cocktail)
            return cocktail
