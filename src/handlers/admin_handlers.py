from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import json
from io import BytesIO

from src.config import config
from src.database import Database
from src.keyboards import *
from src.states import AddCocktail, EditCocktail
from src.filters import IsAdminFilter

router = Router()
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())

# ========== ADMIN MENU ==========
@router.message(F.text == "➕ Добавить коктейль")
async def add_cocktail_start(message: Message, state: FSMContext):
    await message.answer("Введите название коктейля:", reply_markup=cancel_keyboard())
    await state.set_state(AddCocktail.name)

@router.message(F.text == "📝 Редактировать")
async def edit_cocktail_list(message: Message):
    cocktails = await Database.get_all_cocktails()
    if cocktails:
        await message.answer(
            "Выберите коктейль для редактирования:",
            reply_markup=cocktails_list_keyboard(cocktails)
        )
    else:
        await message.answer("В базе нет коктейлей", reply_markup=admin_menu())

@router.message(F.text == "🗑️ Удалить коктейль")
async def delete_cocktail_list(message: Message):
    cocktails = await Database.get_all_cocktails()
    if cocktails:
        await message.answer(
            "Выберите коктейль для удаления:",
            reply_markup=cocktails_list_keyboard(cocktails)
        )
    else:
        await message.answer("В базе нет коктейлей", reply_markup=admin_menu())

@router.message(F.text == "📊 Статистика")
async def show_stats(message: Message):
    count = await Database.get_cocktails_count()
    cocktails = await Database.get_all_cocktails()
    
    strong = len([c for c in cocktails if c.strength > 30])
    medium = len([c for c in cocktails if 15 <= c.strength <= 30])
    weak = len([c for c in cocktails if c.strength < 15])
    
    stats_text = (
        f"📊 <b>Статистика базы:</b>\n\n"
        f"<b>Всего коктейлей:</b> {count}\n\n"
        f"<b>По крепости:</b>\n"
        f"• Слабые (до 15°): {weak}\n"
        f"• Средние (15-30°): {medium}\n"
        f"• Крепкие (30+°): {strong}\n\n"
        f"<b>По сложности:</b>\n"
        f"• Легкие: {len([c for c in cocktails if c.difficulty == 'легко'])}\n"
        f"• Средние: {len([c for c in cocktails if c.difficulty == 'средне'])}\n"
        f"• Сложные: {len([c for c in cocktails if c.difficulty == 'сложно'])}"
    )
    
    await message.answer(stats_text, parse_mode="HTML", reply_markup=admin_menu())

@router.message(F.text == "📦 Экспорт базы")
async def export_database(message: Message):
    cocktails = await Database.get_all_cocktails()
    
    if not cocktails:
        await message.answer("Нет данных для экспорта", reply_markup=admin_menu())
        return
    
    cocktails_data = []
    for cocktail in cocktails:
        cocktails_data.append({
            "name": cocktail.name,
            "description": cocktail.description,
            "ingredients": cocktail.ingredients,
            "recipe": cocktail.recipe,
            "tags": cocktail.tags,
            "strength": cocktail.strength,
            "difficulty": cocktail.difficulty,
            "image_url": cocktail.image_url
        })
    
    json_data = json.dumps(cocktails_data, ensure_ascii=False, indent=2)
    
    # Отправляем как файл
    bio = BytesIO()
    bio.write(json_data.encode('utf-8'))
    bio.seek(0)
    
    await message.answer_document(
        document=("cocktails_export.json", bio),
        caption=f"📦 Экспортировано {len(cocktails)} коктейлей"
    )

@router.message(F.text == "📥 Импорт из файла")
async def import_database(message: Message):
    await message.answer(
        "⚠️ Функция импорта временно недоступна.\n\n"
        "Используйте добавление через кнопку ➕ Добавить коктейль\n"
        "или проверьте формат в экспортированном файле.",
        reply_markup=admin_menu()
    )

@router.message(F.text == "👤 Пользовательское меню")
async def to_user_menu(message: Message):
    await message.answer(
        "Переключение в пользовательское меню:",
        reply_markup=main_menu()
    )

# ========== ADD COCKTAIL STATES ==========
@router.message(AddCocktail.name)
async def add_cocktail_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "Введите описание коктейля (или '-' чтобы пропустить):",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AddCocktail.description)

@router.message(AddCocktail.description)
async def add_cocktail_description(message: Message, state: FSMContext):
    description = None if message.text == "-" else message.text
    await state.update_data(description=description)
    await message.answer(
        "Введите ингредиенты в формате:\n\n"
        "<code>ингредиент: количество</code>\n"
        "<code>ингредиент: количество</code>\n\n"
        "Пример:\n"
        "<code>водка: 50 мл\n"
        "лаймовый сок: 20 мл\n"
        "сахарный сироп: 15 мл</code>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AddCocktail.ingredients)

@router.message(AddCocktail.ingredients)
async def add_cocktail_ingredients(message: Message, state: FSMContext):
    try:
        ingredients = {}
        lines = message.text.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                ingredient, amount = line.split(':', 1)
                ingredients[ingredient.strip()] = amount.strip()
        
        if not ingredients:
            await message.answer("Некорректный формат. Попробуйте снова:")
            return
        
        await state.update_data(ingredients=ingredients)
        await message.answer(
            "Введите рецепт приготовления:",
            reply_markup=cancel_keyboard()
        )
        await state.set_state(AddCocktail.recipe)
        
    except Exception as e:
        await message.answer(f"Ошибка: {e}. Попробуйте снова:")

@router.message(AddCocktail.recipe)
async def add_cocktail_recipe(message: Message, state: FSMContext):
    await state.update_data(recipe=message.text)
    await message.answer(
        "Введите теги через запятую:\n\n"
        "Пример: <code>крепкий, освежающий, летний</code>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AddCocktail.tags)

@router.message(AddCocktail.tags)
async def add_cocktail_tags(message: Message, state: FSMContext):
    tags = [tag.strip() for tag in message.text.split(',') if tag.strip()]
    await state.update_data(tags=tags)
    await message.answer(
        "Введите крепость в градусах (число):",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AddCocktail.strength)

@router.message(AddCocktail.strength)
async def add_cocktail_strength(message: Message, state: FSMContext):
    try:
        strength = int(message.text)
        await state.update_data(strength=strength)
        await message.answer(
            "Выберите сложность приготовления:",
            reply_markup=difficulty_keyboard()
        )
        await state.set_state(AddCocktail.difficulty)
    except ValueError:
        await message.answer("Введите число (например: 40):")

@router.callback_query(AddCocktail.difficulty, F.data.startswith("diff:"))
async def add_cocktail_difficulty(callback: CallbackQuery, state: FSMContext):
    difficulty = callback.data.split(":")[1]
    await state.update_data(difficulty=difficulty)
    
    data = await state.get_data()
    
    preview_text = (
        f"<b>Превью нового коктейля:</b>\n\n"
        f"<b>Название:</b> {data['name']}\n"
        f"<b>Описание:</b> {data.get('description', 'не указано')}\n"
        f"<b>Крепость:</b> {data.get('strength', 0)}°\n"
        f"<b>Сложность:</b> {difficulty}\n"
        f"<b>Теги:</b> {', '.join(data.get('tags', []))}\n\n"
        f"<b>Ингредиентов:</b> {len(data.get('ingredients', {}))}\n\n"
        f"Сохранить коктейль?"
    )
    
    await callback.message.edit_text(
        preview_text,
        reply_markup=yes_no_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(AddCocktail.confirm)
    await callback.answer()

@router.callback_query(AddCocktail.confirm, F.data == "yes")
async def confirm_add_cocktail(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    try:
        cocktail = await Database.add_cocktail(**data)
        
        await callback.message.edit_text(
            f"✅ Коктейль <b>{cocktail.name}</b> успешно добавлен!",
            parse_mode="HTML"
        )
        
        # Показываем добавленный коктейль
        cocktail_text = (
            f"<b>{cocktail.name}</b>\n\n"
            f"<i>{cocktail.description or 'Без описания'}</i>\n\n"
            f"🏷️ Теги: {cocktail.get_tags_text()}\n"
            f"📊 Крепость: {cocktail.strength}°\n"
            f"⚡ Сложность: {cocktail.difficulty}"
        )
        
        await callback.message.answer(
            cocktail_text,
            reply_markup=cocktail_detail_keyboard(cocktail.id, True),
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при добавлении: {str(e)}"
        )
    
    await state.clear()
    await callback.answer()

@router.callback_query(AddCocktail.confirm, F.data == "no")
async def cancel_add_cocktail(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Добавление коктейля отменено")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Действие отменено")
    await state.clear()
    await callback.answer()

# ========== EDIT/DELETE HANDLERS ==========
@router.callback_query(F.data.startswith("edit:"))
async def edit_cocktail_select(callback: CallbackQuery, state: FSMContext):
    cocktail_id = int(callback.data.split(":")[1])
    cocktail = await Database.get_cocktail_by_id(cocktail_id)
    
    if cocktail:
        await state.update_data(edit_cocktail_id=cocktail_id)
        
        edit_text = (
            f"✏️ <b>Редактирование коктейля:</b> {cocktail.name}\n\n"
            f"<b>Выберите что изменить:</b>\n\n"
            f"1. Название: {cocktail.name}\n"
            f"2. Описание: {cocktail.description or 'нет'}\n"
            f"3. Ингредиенты: {len(cocktail.ingredients)} шт.\n"
            f"4. Рецепт\n"
            f"5. Теги: {', '.join(cocktail.tags) if cocktail.tags else 'нет'}\n"
            f"6. Крепость: {cocktail.strength}°\n\n"
            f"Введите номер поля (1-6):"
        )
        
        await callback.message.edit_text(
            edit_text,
            parse_mode="HTML"
        )
        await state.set_state(EditCocktail.select_field)
    else:
        await callback.answer("Коктейль не найден")
    
    await callback.answer()

@router.message(EditCocktail.select_field)
async def edit_cocktail_field(message: Message, state: FSMContext):
    try:
        field_num = int(message.text)
        field_map = {
            1: "name",
            2: "description", 
            3: "ingredients",
            4: "recipe",
            5: "tags",
            6: "strength"
        }
        
        if field_num not in field_map:
            await message.answer("Введите число от 1 до 6:")
            return
        
        await state.update_data(edit_field=field_map[field_num])
        
        field_names = {
            "name": "название",
            "description": "описание",
            "ingredients": "ингредиенты",
            "recipe": "рецепт",
            "tags": "теги",
            "strength": "крепость"
        }
        
        await message.answer(
            f"Введите новое значение для <b>{field_names[field_map[field_num]]}</b>:",
            parse_mode="HTML"
        )
        await state.set_state(EditCocktail.enter_value)
        
    except ValueError:
        await message.answer("Введите число от 1 до 6:")

@router.message(EditCocktail.enter_value)
async def edit_cocktail_value(message: Message, state: FSMContext):
    data = await state.get_data()
    cocktail_id = data['edit_cocktail_id']
    field = data['edit_field']
    value = message.text
    
    update_data = {}
    
    if field == "strength":
        try:
            update_data[field] = int(value)
        except:
            await message.answer("Введите число:")
            return
    elif field == "tags":
        update_data[field] = [tag.strip() for tag in value.split(',') if tag.strip()]
    elif field == "ingredients":
        ingredients = {}
        lines = value.strip().split('\n')
        for line in lines:
            if ':' in line:
                ingredient, amount = line.split(':', 1)
                ingredients[ingredient.strip()] = amount.strip()
        update_data[field] = ingredients
    elif field == "description" and value == "-":
        update_data[field] = None
    else:
        update_data[field] = value
    
    cocktail = await Database.update_cocktail(cocktail_id, **update_data)
    
    if cocktail:
        await message.answer(
            f"✅ Поле <b>{field}</b> успешно обновлено!",
            parse_mode="HTML"
        )
        
        # Показываем обновленный коктейль
        cocktail_text = (
            f"<b>{cocktail.name}</b>\n\n"
            f"<i>{cocktail.description or 'Без описания'}</i>\n\n"
            f"🏷️ Теги: {cocktail.get_tags_text()}\n"
            f"📊 Крепость: {cocktail.strength}°\n"
            f"⚡ Сложность: {cocktail.difficulty}"
        )
        
        await message.answer(
            cocktail_text,
            reply_markup=cocktail_detail_keyboard(cocktail.id, True),
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ Ошибка при обновлении")
    
    await state.clear()

@router.callback_query(F.data.startswith("delete:"))
async def delete_cocktail_confirm(callback: CallbackQuery):
    cocktail_id = int(callback.data.split(":")[1])
    cocktail = await Database.get_cocktail_by_id(cocktail_id)
    
    if cocktail:
        await callback.message.edit_text(
            f"❓ Вы уверены, что хотите удалить коктейль <b>{cocktail.name}</b>?\n\n"
            f"Это действие нельзя отменить!",
            reply_markup=confirm_delete_keyboard(cocktail_id),
            parse_mode="HTML"
        )
    else:
        await callback.answer("Коктейль не найден")
    
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_delete:"))
async def delete_cocktail_execute(callback: CallbackQuery):
    cocktail_id = int(callback.data.split(":")[1])
    cocktail = await Database.get_cocktail_by_id(cocktail_id)
    
    if cocktail:
        await Database.delete_cocktail(cocktail_id)
        await callback.message.edit_text(
            f"✅ Коктейль <b>{cocktail.name}</b> удален",
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text("❌ Коктейль не найден")
    
    await callback.answer()

@router.callback_query(F.data == "cancel_delete")
async def delete_cocktail_cancel(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("Удаление отменено")
