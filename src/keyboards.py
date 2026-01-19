from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# ========== REPLY KEYBOARDS ==========
def main_menu() -> ReplyKeyboardMarkup:
    """Главное меню для пользователей"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="🔍 Найти коктейль"),
    )
    builder.row(
        KeyboardButton(text="🎲 Случайный"),
        KeyboardButton(text="📚 Все коктейли")
    )
    builder.row(
        KeyboardButton(text="ℹ️ О боте"),
    )
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие..."
    )

def admin_menu() -> ReplyKeyboardMarkup:
    """Меню для администраторов"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="➕ Добавить коктейль"),
    )
    builder.row(
        KeyboardButton(text="📝 Редактировать"),
        KeyboardButton(text="🗑️ Удалить")
    )
    builder.row(
        KeyboardButton(text="📊 Статистика"),
        KeyboardButton(text="📦 Экспорт")
    )
    builder.row(
        KeyboardButton(text="👤 В меню"),
    )
    
    return builder.as_markup(resize_keyboard=True)

# ========== INLINE KEYBOARDS ==========
def cocktails_list_keyboard(cocktails, page=0, per_page=5):
    """Клавиатура со списком коктейлей"""
    if not cocktails:
        return None
    
    builder = InlineKeyboardBuilder()
    
    start = page * per_page
    end = start + per_page
    
    # Добавляем коктейли на текущей странице
    for cocktail in cocktails[start:end]:
        builder.row(
            InlineKeyboardButton(
                text=f"🍸 {cocktail.name}",
                callback_data=f"view:{cocktail.id}"
            )
        )
    
    # Кнопки навигации
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page:{page-1}")
        )
    
    if end < len(cocktails):
        nav_buttons.append(
            InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page:{page+1}")
        )
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    # Кнопка возврата в меню
    builder.row(
        InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()

def cocktail_detail_keyboard(cocktail_id, is_admin=False):
    """Клавиатура для детального просмотра коктейля"""
    builder = InlineKeyboardBuilder()
    
    # Основные кнопки
    builder.row(
        InlineKeyboardButton(text="📋 Ингредиенты", callback_data=f"ingr:{cocktail_id}"),
        InlineKeyboardButton(text="👨‍🍳 Рецепт", callback_data=f"recipe:{cocktail_id}")
    )
    
    # Кнопки админа
    if is_admin:
        builder.row(
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit:{cocktail_id}"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete:{cocktail_id}")
        )
    
    # Дополнительные кнопки
    builder.row(
        InlineKeyboardButton(text="🎲 Другой случайный", callback_data="random"),
        InlineKeyboardButton(text="🔙 Назад к списку", callback_data="back_to_list")
    )
    
    return builder.as_markup()

def confirm_delete_keyboard(cocktail_id):
    """Клавиатура подтверждения удаления"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete:{cocktail_id}"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_delete")
    )
    
    return builder.as_markup()

def difficulty_keyboard():
    """Клавиатура выбора сложности"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👶 Легко", callback_data="diff:легко"),
        InlineKeyboardButton(text="👨 Средне", callback_data="diff:средне")
    )
    builder.row(
        InlineKeyboardButton(text="👨‍🍳 Сложно", callback_data="diff:сложно")
    )
    
    return builder.as_markup()

def cancel_keyboard():
    """Кнопка отмены"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    return builder.as_markup()

def yes_no_keyboard():
    """Кнопки Да/Нет"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data="yes"),
        InlineKeyboardButton(text="❌ Нет", callback_data="no")
    )
    
    return builder.as_markup()

def back_keyboard():
    """Кнопка возврата"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back"))
    return builder.as_markup()
