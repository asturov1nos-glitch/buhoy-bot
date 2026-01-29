from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, JSON, Integer, select
from typing import Optional
from datetime import datetime
import json
import logging
import random

from src.config import config

logger = logging.getLogger(__name__)

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
    async def add_cocktail(name, description, ingredients, recipe, tags, strength, difficulty):
        async with async_session() as session:
            cocktail = Cocktail(
                name=name,
                description=description,
                ingredients=ingredients,
                recipe=recipe,
                tags=tags,
                strength=strength,
                difficulty=difficulty
            )
            session.add(cocktail)
            await session.commit()
            await session.refresh(cocktail)
            return cocktail
    
    @staticmethod
    async def get_all_cocktails():
        async with async_session() as session:
            result = await session.execute(select(Cocktail))
            return list(result.scalars().all())
    
    @staticmethod
    async def get_cocktail_by_id(cocktail_id):
        async with async_session() as session:
            result = await session.execute(select(Cocktail).where(Cocktail.id == cocktail_id))
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_random_cocktail():
        async with async_session() as session:
            result = await session.execute(select(Cocktail))
            cocktails = list(result.scalars().all())
            return random.choice(cocktails) if cocktails else None
    
    @staticmethod
    async def get_cocktails_count():
        async with async_session() as session:
            result = await session.execute(select(Cocktail))
            return len(list(result.scalars().all()))

    @staticmethod
    async def search_cocktails(query):
        async with async_session() as session:
            result = await session.execute(select(Cocktail))
            cocktails = list(result.scalars().all())
            query_lower = query.lower()
            found = []
            for cocktail in cocktails:
                # Безопасная проверка с учетом возможных None значений
                name_match = query_lower in cocktail.name.lower() if cocktail.name else False
                
                # Описание может быть None!
                desc_match = False
                if cocktail.description:
                    desc_match = query_lower in cocktail.description.lower()
                
                # Теги могут быть пустым списком
                tags_match = False
                if cocktail.tags:
                    tags_match = any(query_lower in tag.lower() for tag in cocktail.tags)
                
                # Ингредиенты могут быть пустым словарем
                ing_match = False
                if cocktail.ingredients:
                    ing_match = any(query_lower in ing.lower() for ing in cocktail.ingredients.keys())
                
                if name_match or desc_match or tags_match or ing_match:
                    found.append(cocktail)
            return found
