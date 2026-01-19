from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
import logging

from src.config import config
from src.database import Database
from src.keyboards import *
from src.states import SearchCocktail

router = Router()
logger = logging.getLogger(__name__)

# ========== COMMANDS ==========
@router.message(CommandStart())
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

# ========== MAIN MENU HANDLERS ==========
@router.message(F.text == "🔍 Найти коктейль")
async def search_cocktail(message: Message, state: FSMContext):
    logger.info(f"User {message.from_user.id} clicked 'Find cocktail'")
    await message.answer(
        "Введите название коктейля или ингредиент для поиска:",
        reply_markup=None
    )
    await state.set_state(SearchCocktail.by_name)

@router.message(F.text == "🎲 Случайный")
async def random_cocktail(message: Message):
    logger.info(f"User {message.from_user.id} clicked 'Random cocktail'")
    
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
    
    try:
        cocktails = await Database.get_all_cocktails()
        
        if cocktails:
            await message.answer(
                f"📚 Все коктейли ({len(cocktails)} шт.):",
                reply_markup=cocktails_list_keyboard(cocktails)
            )
        else:
            await message.answer(
                "В базе пока нет коктейлей 😔",
                reply_markup=main_menu()
            )
    except Exception as e:
        logger.error(f"Error getting all cocktails: {e}")
        await message.answer(
            "Произошла ошибка. Попробуйте позже.",
            reply_markup=main_menu()
        )

@router.message(F.text == "ℹ️ О боте")
async def about_bot(message: Message):
    logger.info(f"User {message.from_user.id} clicked 'About'")
    
    try:
        count = await Database.get_cocktails_count()
        await message.answer(
            f"🤖 <b>Бот с рецептами коктейлей</b>\n\n"
            f"<b>Количество рецептов:</b> {count}\n\n"
            f"<b>Возможности:</b>\n"
            f"• 🔍 Поиск коктейлей по названию\n"
            f"• 🍸 Поиск по ингредиентам\n"
            f"• 🎲 Случайный коктейль\n"
            f"• 📚 Просмотр всех рецептов\n\n"
            f"База постоянно пополняется!",
            parse_mode="HTML",
            reply_markup=main_menu()
        )
    except Exception as e:
        logger.error(f"Error in about: {e}")
        await message.answer(
            "🤖 Бот с рецептами коктейлей\nИспользуйте кнопки для навигации.",
            reply_markup=main_menu()
        )

# ========== SEARCH HANDLERS ==========
@router.message(SearchCocktail.by_name)
async def process_search(message: Message, state: FSMContext):
    search_text = message.text.strip()
    logger.info(f"User {message.from_user.id} searching for: {search_text}")
    
    if not search_text:
        await message.answer(
            "Пожалуйста, введите текст для поиска:",
            reply_markup=main_menu()
        )
        await state.clear()
        return
    
    try:
        # Сначала ищем по названию
        cocktails = await Database.search_cocktails(name=search_text)
        
        # Если не нашли по названию, ищем по ингредиенту
        if not cocktails:
            cocktails = await Database.search_cocktails(ingredient=search_text)
        
        if cocktails:
            if len(cocktails) == 1:
                # Если найден один коктейль - показываем его
                await show_cocktail(message, cocktails[0], message.from_user.id in config.ADMIN_IDS)
            else:
                # Если несколько - показываем список
                await message.answer(
                    f"🔍 Найдено {len(cocktails)} коктейлей по запросу '<i>{search_text}</i>':",
                    parse_mode="HTML",
                    reply_markup=cocktails_list_keyboard(cocktails)
                )
        else:
            await message.answer(
                f"Коктейли по запросу '<i>{search_text}</i>' не найдены 😔\n\n"
                f"Попробуйте:\n"
                f"• Упростить запрос\n"
                f"• Искать по другому ингредиенту\n"
                f"• Посмотреть случайный коктейль",
                parse_mode="HTML",
                reply_markup=main_menu()
            )
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        await message.answer(
            "Произошла ошибка при поиске. Попробуйте позже.",
            reply_markup=main_menu()
        )
    
    await state.clear()

# ========== CALLBACK HANDLERS ==========
@router.callback_query(F.data.startswith("view:"))
async def view_cocktail(callback: CallbackQuery):
    try:
        cocktail_id = int(callback.data.split(":")[1])
        cocktail = await Database.get_cocktail_by_id(cocktail_id)
        
        if cocktail:
            await show_cocktail(callback.message, cocktail, callback.from_user.id in config.ADMIN_IDS)
        else:
            await callback.answer("Коктейль не найден")
    except Exception as e:
        logger.error(f"Error viewing cocktail: {e}")
        await callback.answer("Ошибка при загрузке коктейля")
    
    await callback.answer()

@router.callback_query(F.data.startswith("ingr:"))
async def show_ingredients(callback: CallbackQuery):
    try:
        cocktail_id = int(callback.data.split(":")[1])
        cocktail = await Database.get_cocktail_by_id(cocktail_id)
        
        if cocktail:
            await callback.message.edit_text(
                f"📋 <b>Ингредиенты для {cocktail.name}:</b>\n\n"
                f"{cocktail.get_ingredients_text()}",
                parse_mode="HTML",
                reply_markup=cocktail_detail_keyboard(cocktail_id, callback.from_user.id in config.ADMIN_IDS)
            )
    except Exception as e:
        logger.error(f"Error showing ingredients: {e}")
        await callback.answer("Ошибка")
    
    await callback.answer()

@router.callback_query(F.data.startswith("recipe:"))
async def show_recipe(callback: CallbackQuery):
    try:
        cocktail_id = int(callback.data.split(":")[1])
        cocktail = await Database.get_cocktail_by_id(cocktail_id)
        
        if cocktail:
            await callback.message.edit_text(
                f"👨‍🍳 <b>Рецепт {cocktail.name}:</b>\n\n"
                f"{cocktail.recipe}\n\n"
                f"<b>Сложность:</b> {cocktail.difficulty}",
                parse_mode="HTML",
                reply_markup=cocktail_detail_keyboard(cocktail_id, callback.from_user.id in config.ADMIN_IDS)
            )
    except Exception as e:
        logger.error(f"Error showing recipe: {e}")
        await callback.answer("Ошибка")
    
    await callback.answer()

@router.callback_query(F.data == "random")
async def another_random(callback: CallbackQuery):
    try:
        cocktail = await Database.get_random_cocktail()
        if cocktail:
            await show_cocktail(callback.message, cocktail, callback.from_user.id in config.ADMIN_IDS)
        else:
            await callback.answer("Нет коктейлей в базе")
    except Exception as e:
        logger.error(f"Error getting random cocktail in callback: {e}")
        await callback.answer("Ошибка")
    
    await callback.answer()

@router.callback_query(F.data.startswith("page:"))
async def change_page(callback: CallbackQuery):
    try:
        page = int(callback.data.split(":")[1])
        cocktails = await Database.get_all_cocktails()
        await callback.message.edit_reply_markup(
            reply_markup=cocktails_list_keyboard(cocktails, page)
        )
    except Exception as e:
        logger.error(f"Error changing page: {e}")
        await callback.answer("Ошибка")
    
    await callback.answer()

@router.callback_query(F.data == "back_to_list")
async def back_to_list(callback: CallbackQuery):
    try:
        cocktails = await Database.get_all_cocktails()
        await callback.message.edit_text(
            f"📚 Все коктейли ({len(cocktails)} шт.):",
            reply_markup=cocktails_list_keyboard(cocktails)
        )
    except Exception as e:
        logger.error(f"Error back to list: {e}")
        await callback.answer("Ошибка")
    
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    try:
        await callback.message.delete()
        await callback.message.answer(
            "Главное меню:",
            reply_markup=main_menu()
        )
    except Exception as e:
        logger.error(f"Error returning to main menu: {e}")
    
    await callback.answer()

# ========== HELPER FUNCTIONS ==========
async def show_cocktail(message, cocktail, is_admin=False):
    """Показать информацию о коктейле"""
    try:
        cocktail_text = (
            f"<b>{cocktail.name}</b>\n\n"
            f"<i>{cocktail.description or 'Нет описания'}</i>\n\n"
            f"<b>Теги:</b> {cocktail.get_tags_text()}\n"
            f"<b>Крепость:</b> {cocktail.strength}°\n"
            f"<b>Сложность:</b> {cocktail.difficulty}"
        )
        
        # Проверяем, можем ли редактировать сообщение
        if hasattr(message, 'edit_text'):
            try:
                await message.edit_text(
                    cocktail_text,
                    parse_mode="HTML",
                    reply_markup=cocktail_detail_keyboard(cocktail.id, is_admin)
                )
                return
            except:
                # Если не удалось редактировать, отправляем новое сообщение
                pass
        
        # Отправляем новое сообщение
        await message.answer(
            cocktail_text,
            parse_mode="HTML",
            reply_markup=cocktail_detail_keyboard(cocktail.id, is_admin)
        )
        
    except Exception as e:
        logger.error(f"Error showing cocktail {cocktail.name}: {e}")
        raise

# ========== DEBUG HANDLER ==========
@router.message()
async def debug_handler(message: Message):
    """Обработчик для отладки необработанных сообщений"""
    logger.info(f"Unhandled message from {message.from_user.id}: {message.text}")
    await message.answer(
        "Я не понял ваше сообщение. Используйте кнопки меню или команды.",
        reply_markup=main_menu()
    )
