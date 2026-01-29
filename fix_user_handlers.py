with open('src/handlers/user_handlers.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    # Ищем обработчик "Я не понял"
    if 'Я не понял' in line:
        print(f"Нашел обработчик на строке {i+1}")
        # Пропускаем этот обработчик
        skip = True
    elif skip and '@router.message()' in line and i > 0:
        # Нашли новый обработчик - заканчиваем пропуск
        skip = False
        new_lines.append(line)
    elif not skip:
        new_lines.append(line)

with open('src/handlers/user_handlers.py', 'w') as f:
    f.writelines(new_lines)
    
print("✅ Обработчик 'Я не понял' удален")
