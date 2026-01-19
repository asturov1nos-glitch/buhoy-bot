from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, JSON, Integer, Boolean
from typing import Optional
from datetime import datetime
import json

from src.config import config

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
    async def add_cocktail(**kwargs):
        async with async_session() as session:
            cocktail = Cocktail(**kwargs)
            session.add(cocktail)
            await session.commit()
            await session.refresh(cocktail)
            return cocktail
    
    @staticmethod
    async def get_cocktail_by_id(cocktail_id: int):
        async with async_session() as session:
            return await session.get(Cocktail, cocktail_id)
    
    @staticmethod
    async def get_cocktail_by_name(name: str):
        async with async_session() as session:
            from sqlalchemy import select
            query = select(Cocktail).where(Cocktail.name.ilike(f"%{name}%"))
            result = await session.execute(query)
            return result.scalars().all()
    
    @staticmethod
    async def get_all_cocktails():
        async with async_session() as session:
            from sqlalchemy import select
            query = select(Cocktail).order_by(Cocktail.name)
            result = await session.execute(query)
            return result.scalars().all()
    
    @staticmethod
    async def search_cocktails(**kwargs):
        async with async_session() as session:
            from sqlalchemy import select, and_
            conditions = []
            
            if name := kwargs.get('name'):
                conditions.append(Cocktail.name.ilike(f"%{name}%"))
            if ingredient := kwargs.get('ingredient'):
                conditions.append(Cocktail.ingredients.cast(String).ilike(f"%{ingredient}%"))
            if tag := kwargs.get('tag'):
                conditions.append(Cocktail.tags.cast(String).ilike(f"%{tag}%"))
            if max_strength := kwargs.get('max_strength'):
                conditions.append(Cocktail.strength <= max_strength)
            
            query = select(Cocktail).where(and_(*conditions)).order_by(Cocktail.name)
            result = await session.execute(query)
            return result.scalars().all()
    
    @staticmethod
    async def update_cocktail(cocktail_id: int, **kwargs):
        async with async_session() as session:
            cocktail = await session.get(Cocktail, cocktail_id)
            if cocktail:
                for key, value in kwargs.items():
                    setattr(cocktail, key, value)
                await session.commit()
                await session.refresh(cocktail)
            return cocktail
    
    @staticmethod
    async def delete_cocktail(cocktail_id: int):
        async with async_session() as session:
            cocktail = await session.get(Cocktail, cocktail_id)
            if cocktail:
                await session.delete(cocktail)
                await session.commit()
                return True
            return False
    
    @staticmethod
    async def get_random_cocktail():
        async with async_session() as session:
            from sqlalchemy import select, func
            query = select(Cocktail).order_by(func.random()).limit(1)
            result = await session.execute(query)
            return result.scalar()
    
    @staticmethod
    async def get_cocktails_count():
        async with async_session() as session:
            from sqlalchemy import select, func
            query = select(func.count(Cocktail.id))
            result = await session.execute(query)
            return result.scalar()
