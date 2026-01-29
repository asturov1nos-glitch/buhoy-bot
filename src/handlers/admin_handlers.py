from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import StateFilter

from src.config import config
from src.database import Database
from src.keyboards import *
from src.states import AddCocktail
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(F.text == "👤 В меню")
async def back_to_main_menu(message: Message):
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer("Админ-панель:", reply_markup=admin_menu())
    else:
        await message.answer("Меню:", reply_markup=main_menu())

@router.message(F.text == "➕ Добавить коктейль")
async def add_cocktail_start(message: Message, state: FSMContext):
    await message.answer(
        "Введите название коктейля:\n"
        "<i>Пример: Мохито, Маргарита, Дайкири</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AddCocktail.name)

@router.message(StateFilter(AddCocktail.name))
async def process_name(message: Message, state: FSMContext):
    if len(message.text) > 100:
        await message.answer("Название слишком длинное (макс 100 символов). Введите снова:")
        return
    await state.update_data(name=message.text)
    await message.answer(
        "Введите описание коктейля (можно пропустить, отправьте '-'):",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AddCocktail.description)

@router.message(StateFilter(AddCocktail.description))
async def process_description(message: Message, state: FSMContext):
    description = "" if message.text == "-" else message.text
    await state.update_data(description=description)
    await message.answer(
        "Введите ингредиенты в формате:\n"
        "<code>ингредиент: количество\nингредиент: количество</code>\n\n"
        "<i>Пример:\nром: 50 мл\nлайм: 1/2 шт\nмята: 6 листьев</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AddCocktail.ingredients)

@router.message(StateFilter(AddCocktail.ingredients))
async def process_ingredients(message: Message, state: FSMContext):
    try:
        ingredients = {}
        lines = [line.strip() for line in message.text.split('\n') if line.strip()]
        for line in lines:
            if ':' in line:
                ingredient, amount = line.split(':', 1)
                ingredients[ingredient.strip()] = amount.strip()
            else:
                await message.answer("❌ Неправильный формат. Используйте 'ингредиент: количество'")
                return
        if not ingredients:
            await message.answer("❌ Нет ингредиентов. Введите хотя бы один:")
            return
        await state.update_data(ingredients=ingredients)
        await message.answer(
            "Введите рецепт приготовления:",
            reply_markup=cancel_keyboard()
        )
        await state.set_state(AddCocktail.recipe)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}. Введите ингредиенты снова:")
        return

@router.message(StateFilter(AddCocktail.recipe))
async def process_recipe(message: Message, state: FSMContext):
    await state.update_data(recipe=message.text)
    await message.answer(
        "Введите теги через запятую:\n"
        "<i>Пример: освежающий, летний, ромовый, алкогольный</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AddCocktail.tags)

@router.message(StateFilter(AddCocktail.tags))
async def process_tags(message: Message, state: FSMContext):
    tags = [tag.strip() for tag in message.text.split(',') if tag.strip()]
    await state.update_data(tags=tags)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Слабоалкогольный (0-15°)", callback_data="strength:10"),
        InlineKeyboardButton(text="Средний (16-25°)", callback_data="strength:20")
    )
    builder.row(
        InlineKeyboardButton(text="Крепкий (26-40°)", callback_data="strength:35"),
        InlineKeyboardButton(text="Безалкогольный", callback_data="strength:0")
    )
    
    await message.answer("Выберите крепость:", reply_markup=builder.as_markup())
    await state.set_state(AddCocktail.strength)

@router.callback_query(StateFilter(AddCocktail.strength), F.data.startswith("strength:"))
async def process_strength(callback: CallbackQuery, state: FSMContext):
    strength = int(callback.data.split(":")[1])
    await state.update_data(strength=strength)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Легко", callback_data="difficulty:легко"),
        InlineKeyboardButton(text="Средне", callback_data="difficulty:средне"),
        InlineKeyboardButton(text="Сложно", callback_data="difficulty:сложно")
    )
    
    await callback.message.answer("Выберите сложность:", reply_markup=builder.as_markup())
    await state.set_state(AddCocktail.difficulty)
    await callback.answer()

@router.callback_query(StateFilter(AddCocktail.difficulty), F.data.startswith("difficulty:"))
async def process_difficulty(callback: CallbackQuery, state: FSMContext):
    difficulty = callback.data.split(":")[1]
    await state.update_data(difficulty=difficulty)
    
    data = await state.get_data()
    
    # УДАЛЯЕМ editing_field если есть
    data.pop('editing_field', None)
    
    preview = (
        f"<b>📋 ПРЕДПРОСМОТР КОКТЕЙЛЯ</b>\n\n"
        f"<b>Название:</b> {data['name']}\n"
        f"<b>Описание:</b> {data.get('description', 'нет')}\n"
        f"<b>Крепость:</b> {data['strength']}°\n"
        f"<b>Сложность:</b> {data['difficulty']}\n"
        f"<b>Теги:</b> {', '.join(data['tags']) if data['tags'] else 'нет'}\n\n"
        f"<b>Ингредиенты:</b>\n"
    )
    
    for ingredient, amount in data['ingredients'].items():
        preview += f"• {ingredient}: {amount}\n"
    
    preview += f"\n<b>Рецепт:</b>\n{data['recipe']}"
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Сохранить", callback_data="save_cocktail"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_add")
    )
    
    await callback.message.answer(preview, parse_mode="HTML", reply_markup=builder.as_markup())
    await state.set_state(AddCocktail.confirm)
    await callback.answer()

@router.callback_query(StateFilter(AddCocktail.confirm), F.data == "save_cocktail")
async def save_cocktail(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # УДАЛЯЕМ ВСЕ ЛИШНИЕ ПОЛЯ
    cocktail_data = {
        'name': data.get('name'),
        'description': data.get('description', ''),
        'ingredients': data.get('ingredients'),
        'recipe': data.get('recipe'),
        'tags': data.get('tags', []),
        'strength': data.get('strength'),
        'difficulty': data.get('difficulty')
    }
    
    # Проверяем обязательные поля
    required = ['name', 'ingredients', 'recipe', 'strength', 'difficulty']
    for field in required:
        if not cocktail_data[field]:
            await callback.message.answer(f"❌ Отсутствует поле: {field}")
            await state.clear()
            return
    
    try:
        cocktail = await Database.add_cocktail(**cocktail_data)
        
        await callback.message.answer(
            f"✅ Коктейль <b>{cocktail.name}</b> успешно добавлен!\n"
            f"Всего коктейлей: {await Database.get_cocktails_count()}",
            parse_mode="HTML"
        )
        
        text = (
            f"<b>{cocktail.name}</b>\n\n"
            f"<i>{cocktail.description or 'Нет описания'}</i>\n\n"
            f"<b>Теги:</b> {cocktail.get_tags_text()}\n"
            f"<b>Крепость:</b> {cocktail.strength}°\n"
            f"<b>Сложность:</b> {cocktail.difficulty}"
        )
        
        await callback.message.answer(text, parse_mode="HTML")
        
    except Exception as e:
        await callback.message.answer(
            f"❌ Ошибка при сохранении: {e}\n"
            "Возможно, коктейль с таким названием уже существует."
        )
    
    await state.clear()
    await callback.answer()

@router.callback_query(StateFilter(AddCocktail.confirm), F.data == "cancel_add")
async def cancel_add_cocktail(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Добавление отменено.")
    await callback.answer()
