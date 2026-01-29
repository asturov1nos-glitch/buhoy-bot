with open('src/database.py', 'r') as f:
    lines = f.readlines()

# Найдем метод add_cocktail
for i, line in enumerate(lines):
    if 'async def add_cocktail' in line:
        start = i
        # Найдем конец метода
        for j in range(i, len(lines)):
            if j > i and lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                end = j
                break
        else:
            end = len(lines)
        
        # Заменяем метод
        new_method = '''    @staticmethod
    async def add_cocktail(name, description, ingredients, recipe, tags, strength, difficulty, image_url=None):
        async with async_session() as session:
            cocktail = Cocktail(
                name=name,
                description=description,
                ingredients=ingredients,
                recipe=recipe,
                tags=tags,
                strength=strength,
                difficulty=difficulty,
                image_url=image_url
            )
            session.add(cocktail)
            await session.commit()
            await session.refresh(cocktail)
            return cocktail
'''
        # Заменяем строки
        lines[start:end] = [new_method]
        break

with open('src/database.py', 'w') as f:
    f.writelines(lines)

print("✅ Метод add_cocktail исправлен")
