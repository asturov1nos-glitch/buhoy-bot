from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from src.config import config
from src.database import Database
from src.keyboards import *
import logging

logger = logging.getLogger(__name__)

router = Router()

# ========== КОМАНДЫ ==========
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
            "🍸 Добро пожаловать в бот с рецептами коктейлей!\n"
            "Выберите действие:",
            reply_markup=main_menu()
        )

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    logger.info(f"User {message.from_user.id} requested admin panel")
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer("Админ-панель:", reply_markup=admin_menu())
    else:
        await message.answer("У вас нет прав доступа")

# ========== ГЛАВНОЕ МЕНЮ ==========
@router.message(F.text == "🔍 Найти коктейль")
async def search_cocktail(message: Message, state: FSMContext):
    logger.info(f"User {message.from_user.id} clicked 'Find cocktail'")
    await message.answer(
        "Введите название коктейля или ингредиент для поиска:",
        reply_markup=cancel_keyboard()
    )
    await state.set_state("waiting_search")

@router.message(F.text == "🎲 Случайный")
async def random_cocktail(message: Message):
    logger.info(f"User {message.from_user.id} clicked 'Random'")
    try:
        cocktail = await Database.get_random_cocktail()
        if cocktail:
            await show_cocktail(message, cocktail, message.from_user.id in config.ADMIN_IDS)
        else:
            await message.answer(
                "В базе пока нет коктейлей 😔\n\n"
                "Администратор может добавить коктейли через админ-панель.",
                reply_markup=main_menu()
            )
    except Exception as e:
        logger.error(f"Error getting random cocktail: {e}")
        await message.answer(
            "Произошла ошибка при получении коктейля. Попробуйте позже.",
            reply_markup=main_menu()
        )

@router.message(F.text == "📚 Все коктейли")
async def all_cocktails(message: Message):
    logger.info(f"User {message.from_user.id} clicked 'All cocktails'")
    cocktails = await Database.get_all_cocktails()
    if cocktails:
        await message.answer(
            f"📚 Все коктейли ({len(cocktails)} шт.):",
            reply_markup=cocktails_list_keyboard(cocktails)
        )
    else:
        await message.answer(
            "В базе пока нет коктейлей 😔\n\n"
            "Администратор может добавить коктейли через админ-панель.",
            reply_markup=main_menu()
        )

@router.message(F.text == "ℹ️ О боте")
async def about_bot(message: Message):
    logger.info(f"User {message.from_user.id} clicked 'About'")
    await message.answer(
        "🤖 <b>Cocktail Bot</b>\n\n"
        "Этот бот поможет вам найти рецепты коктейлей!\n\n"
        "<b>Функции:</b>\n"
        "• Поиск коктейлей по названию или ингредиентам\n"
        "• Случайный коктейль\n"
        "• Полный список коктейлей\n"
        "• Админ-панель для добавления/редактирования\n\n"
        "<b>Разработчик:</b> @asturov1nos",
        parse_mode="HTML"
    )

# ========== ПОИСК ==========
@router.message(F.text == "🔙 Отмена")
async def cancel_search(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer("Поиск отменен", reply_markup=admin_menu())
    else:
        await message.answer("Поиск отменен", reply_markup=main_menu())

# ========== ПОКАЗ КОКТЕЙЛЯ ==========
async def show_cocktail(message: Message, cocktail, is_admin=False):
    text = (
        f"<b>{cocktail.name}</b>\n\n"
        f"<i>{cocktail.description or 'Нет описания'}</i>\n\n"
        f"<b>Теги:</b> {cocktail.get_tags_text()}\n"
        f"<b>Крепость:</b> {cocktail.strength}°\n"
        f"<b>Сложность:</b> {cocktail.difficulty}"
    )
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=cocktail_detail_keyboard(cocktail.id, is_admin=is_admin)
    )

# ========== ОБРАБОТЧИК ВСЕХ СООБЩЕНИЙ (ТОЛЬКО ДЛЯ НЕАДМИНОВ) ==========
@router.message()
async def handle_unknown_message(message: Message):
    # Если пользователь админ - пропускаем, пусть админ-обработчики ловят
    if message.from_user.id in config.ADMIN_IDS:
        return
    
    # Если не админ - показываем сообщение
    await message.answer(
        "Я не понял ваше сообщение. Используйте кнопки меню или команды",
        reply_markup=main_menu()
    )
