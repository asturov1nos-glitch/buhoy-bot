from aiogram.fsm.state import State, StatesGroup

class AddCocktail(StatesGroup):
    name = State()
    description = State()
    ingredients = State()
    recipe = State()
    tags = State()
    strength = State()
    difficulty = State()
    confirm = State()

class EditCocktail(StatesGroup):
    select_cocktail = State()
    select_field = State()
    enter_value = State()

class SearchCocktail(StatesGroup):
    by_name = State()
    by_ingredient = State()
    by_tag = State()

class AdminStates(StatesGroup):
    waiting_for_backup_action = State()
