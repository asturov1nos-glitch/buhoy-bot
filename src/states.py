from aiogram.fsm.state import State, StatesGroup

class AddCocktail(StatesGroup):
    name = State()
    description = State()
    ingredients = State()
    recipe = State()
    tags = State()
    strength = State()
    difficulty = State()
    image = State()
    confirm = State()

class EditCocktail(StatesGroup):
    select_field = State()
    enter_value = State()

class SearchCocktail(StatesGroup):
    by_name = State()
    by_ingredient = State()
    by_tag = State()
