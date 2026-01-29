with open('src/handlers/admin_handlers.py', 'r') as f:
    content = f.read()

# Найдем начало функции save_cocktail
start = content.find('@router.callback_query(StateFilter(AddCocktail.confirm), F.data == "save_cocktail")')
if start == -1:
    print("❌ Не найдена функция save_cocktail")
    exit(1)

# Найдем конец функции (до следующего декоратора @router)
end = content.find('@router.', start + 1)
if end == -1:
    end = len(content)

# Извлекаем функцию
function_text = content[start:end]

# Заменяем старую функцию на исправленную
new_function = '''@router.callback_query(StateFilter(AddCocktail.confirm), F.data == "save_cocktail")
async def save_cocktail(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Удаляем служебные поля, которые не нужны для создания коктейля
    if 'editing_field' in data:
        del data['editing_field']
    
    # Поля, которые должны быть у коктейля
    required_fields = ['name', 'ingredients', 'recipe', 'strength', 'difficulty']
    cocktail_data = {}
    
    for field in required_fields:
        if field not in data:
            await callback.message.answer(f"❌ Отсутствует обязательное поле: {field}")
            await state.clear()
            return
    
    # Собираем данные для коктейля
    cocktail_data = {
        'name': data['name'],
        'description': data.get('description', ''),
        'ingredients': data['ingredients'],
        'recipe': data['recipe'],
        'tags': data.get('tags', []),
        'strength': data['strength'],
        'difficulty': data['difficulty']
    }
    
    try:
        cocktail = await Database.add_cocktail(**cocktail_data)
        
        await callback.message.answer(
            f"✅ Коктейль <b>{cocktail.name}</b> успешно добавлен!\\n"
            f"Всего коктейлей в базе: {await Database.get_cocktails_count()}",
            parse_mode="HTML"
        )
        
        # Показываем коктейль
        text = (
            f"<b>{cocktail.name}</b>\\n\\n"
            f"<i>{cocktail.description or 'Нет описания'}</i>\\n\\n"
            f"<b>Теги:</b> {cocktail.get_tags_text()}\\n"
            f"<b>Крепость:</b> {cocktail.strength}°\\n"
            f"<b>Сложность:</b> {cocktail.difficulty}"
        )
        
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=cocktail_detail_keyboard(cocktail.id, is_admin=True)
        )
        
    except Exception as e:
        await callback.message.answer(
            f"❌ Ошибка при сохранении: {e}\\n"
            "Возможно, коктейль с таким названием уже существует."
        )
    
    await state.clear()
    await callback.answer()
'''

# Заменяем в исходном содержимом
new_content = content[:start] + new_function + content[end:]

with open('src/handlers/admin_handlers.py', 'w') as f:
    f.write(new_content)

print("✅ Функция save_cocktail исправлена")
