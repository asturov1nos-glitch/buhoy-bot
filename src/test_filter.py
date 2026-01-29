# test_filter.py
from src.config import config

print("ADMIN_IDS из конфига:", config.ADMIN_IDS)
print("Тип ADMIN_IDS:", type(config.ADMIN_IDS))
print("860643367 в списке:", 860643367 in config.ADMIN_IDS)

# Проверим, как загружены ID
admin_ids_str = config.ADMIN_IDS
if isinstance(admin_ids_str, str):
    # Пробуем распарсить
    import ast
    try:
        admin_ids = ast.literal_eval(admin_ids_str)
        print("Распарсенные ID:", admin_ids)
        print("860643367 в распарсенных:", 860643367 in admin_ids)
    except:
        # Если не список, а одно число
        try:
            admin_id = int(admin_ids_str.strip())
            print("Единичный ID:", admin_id)
            print("Совпадает?", admin_id == 860643367)
        except:
            print("Не удалось распарсить")