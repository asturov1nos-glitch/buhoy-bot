from src.config import config

print("=== Тест фильтра админа ===")
print("ADMIN_IDS из конфига:", config.ADMIN_IDS)
print("Тип ADMIN_IDS:", type(config.ADMIN_IDS))

# Проверим, как загружены ID
admin_ids_value = config.ADMIN_IDS

if isinstance(admin_ids_value, list):
    print("ADMIN_IDS - это список")
    print("860643367 в списке:", 860643367 in admin_ids_value)
elif isinstance(admin_ids_value, str):
    print("ADMIN_IDS - это строка")
    # Пробуем распарсить
    try:
        import ast
        admin_ids = ast.literal_eval(admin_ids_value)
        print("Распарсенные ID:", admin_ids)
        print("860643367 в распарсенных:", 860643367 in admin_ids)
    except:
        # Если не список, а одно число
        try:
            admin_id = int(admin_ids_value.strip())
            print("Единичный ID:", admin_id)
            print("Совпадает?", admin_id == 860643367)
        except:
            print("Не удалось распарсить строку")
else:
    print("Неизвестный тип")
