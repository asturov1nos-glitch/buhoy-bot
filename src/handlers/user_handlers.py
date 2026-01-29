from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.config import config
from src.database import Database
from src.keyboards import *
import logging

logger = logging.getLogger(__name__)

router = Router()

class SearchStates(StatesGroup):
    waiting_query = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    logger.info(f"User {message.from_user.id} started bot")
    
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer(
            "👑 Добро пожаловать в админ-панель!",
            reply_markup=admin_menu()
        )
    else:
        await message.answer(
            "🍸 Добро пожаловать в бот с рецептами коктейлей!\nВыберите действие:",
            reply_markup=main_menu()
        )

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer("Админ-панель:", reply_markup=admin_menu())
    else:
        await message.answer("У вас нет прав доступа")

# ========== РАБОЧИЕ КНОПКИ ==========

@router.message(F.text == "🎲 Случайный")
async def random_cocktail(message: Message):
    logger.info(f"User {message.from_user.id} clicked 'Случайный'")
    cocktail = await Database.get_random_cocktail()
    if cocktail:
        text = (
            f"<b>{cocktail.name}</b>\n\n"
            f"<i>{cocktail.description or 'Нет описания'}</i>\n\n"
            f"<b>Теги:</b> {cocktail.get_tags_text()}\n"
            f"<b>Крепость:</b> {cocktail.strength}°\n"
            f"<b>Сложность:</b> {cocktail.difficulty}"
        )
        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer("😔 В базе пока нет коктейлей")

@router.message(F.text == "📚 Все коктейли")
async def all_cocktails(message: Message):
    logger.info(f"User {message.from_user.id} clicked 'Все коктейли'")
    cocktails = await Database.get_all_cocktails()
    if cocktails:
        await message.answer(
            f"📚 Все коктейли ({len(cocktails)} шт.):",
            reply_markup=cocktails_list_keyboard(cocktails)
        )
    else:
        await message.answer("😔 В базе пока нет коктейлей")

@router.message(F.text == "🔍 Найти коктейль")
async def search_cocktail_start(message: Message, state: FSMContext):
    logger.info(f"User {message.from_user.id} clicked 'Найти коктейль'")
    await message.answer("Введите название коктейля или ингредиент для поиска:")
    await state.set_state(SearchStates.waiting_query)

@router.message(StateFilter(SearchStates.waiting_query))
async def process_search(message: Message, state: FSMContext):
    query = message.text.strip()
    if not query:
        await message.answer("Пожалуйста, введите поисковый запрос")
        return
    
    cocktails = await Database.search_cocktails(query)
    if cocktails:
        await message.answer(f"🔍 Найдено {len(cocktails)} коктейлей по запросу '{query}':")
        for cocktail in cocktails[:5]:  # Показываем первые 5
            text = (
                f"<b>{cocktail.name}</b>\n"
                f"<i>{cocktail.description[:100] if cocktail.description else ''}...</i>\n"
                f"Теги: {cocktail.get_tags_text()}"
            )
            await message.answer(text, parse_mode="HTML")
    else:
        await message.answer(f"😔 Не найдено коктейлей по запросу '{query}'")
    
    await state.clear()

@router.message(F.text == "ℹ️ О боте")
async def about_bot(message: Message):
    await message.answer(
        "🤖 <b>Cocktail Bot</b>\n\n"
        "Бот для поиска рецептов коктейлей.\n\n"
        "Функции:\n"
        "• Поиск коктейлей\n"
        "• Случайный коктейль\n"
        "• Полный список\n"
        "• Админ-панель для добавления",
        parse_mode="HTML"
    )

# ========== CALLBACK ОБРАБОТЧИКИ ==========

@router.callback_query(F.data == "main_menu")
async def back_to_main_menu_callback(callback: CallbackQuery):
    await callback.message.answer(
        "🍸 Главное меню:",
        reply_markup=main_menu()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("view:"))
async def view_cocktail_callback(callback: CallbackQuery):
    cocktail_id = int(callback.data.split(":")[1])
    cocktail = await Database.get_cocktail_by_id(cocktail_id)
    if cocktail:
        text = (
            f"<b>{cocktail.name}</b>\n\n"
            f"<i>{cocktail.description or 'Нет описания'}</i>\n\n"
            f"<b>Ингредиенты:</b>\n{cocktail.get_ingredients_text()}\n\n"
            f"<b>Рецепт:</b>\n{cocktail.recipe}\n\n"
            f"<b>Теги:</b> {cocktail.get_tags_text()}\n"
            f"<b>Крепость:</b> {cocktail.strength}°\n"
            f"<b>Сложность:</b> {cocktail.difficulty}"
        )
        await callback.message.answer(text, parse_mode="HTML")
    else:
        await callback.answer("Коктейль не найден")
    await callback.answer()

# Обработчик неизвестных сообщений
@router.message()
async def handle_unknown(message: Message):
    if message.from_user.id in config.ADMIN_IDS:
        return  # Пропускаем для админов
    await message.answer(
        "Я не понял ваше сообщение. Используйте кнопки меню или команды",
        reply_markup=main_menu()
    )
