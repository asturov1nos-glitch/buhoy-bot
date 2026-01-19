from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from src.config import config

class IsAdminFilter(BaseFilter):
    async def __call__(self, update: Message | CallbackQuery) -> bool:
        user_id = update.from_user.id
        return user_id in config.ADMIN_IDS
