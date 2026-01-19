import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from src.config import config
from src.database import Database
from src.handlers import user_router, admin_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log")
    ]
)
logger = logging.getLogger(__name__)

async def initialize_database():
    """Инициализация базы данных"""
    logger.info("Инициализация базы данных...")
    
    try:
        # Создаем таблицы
        await Database.create_tables()
        logger.info("✓ Таблицы созданы/проверены")
        
        # Проверяем, есть ли коктейли в базе
        count = await Database.get_cocktails_count()
        logger.info(f"✓ В базе: {count} коктейлей")
        
        # Если база пуста, добавляем начальные данные
        if count == 0:
            logger.info("База пуста, добавляем начальные данные...")
            await add_initial_cocktails()
            count = await Database.get_cocktails_count()
            logger.info(f"✓ Добавлено {count} коктейлей")
            
        return True
        
    except Exception as e:
        logger.error(f"✗ Ошибка инициализации БД: {e}")
        return False

async def add_initial_cocktails():
    """Добавление начальных коктейлей"""
    initial_cocktails = [
        {
            "name": "Мохито",
            "description": "Освежающий кубинский коктейль с мятой и лаймом",
            "ingredients": {
                "белый ром": "50 мл",
                "свежая мята": "6-8 листиков",
                "лайм": "половинка",
                "сахарный сироп": "20 мл",
                "содовая": "100 мл",
                "лед": "дробленый"
            },
            "recipe": "1. В высокий бокал положите мяту и лайм\n2. Добавьте сахарный сироп и аккуратно подавите\n3. Наполните бокал дробленым льдом\n4. Добавьте ром и содовую\n5. Аккуратно перемешайте",
            "tags": ["освежающий", "летний", "мятный", "цитрусовый"],
            "strength": 15,
            "difficulty": "легко"
        },
        {
            "name": "Маргарита",
            "description": "Классический коктейль с текилой и лаймом",
            "ingredients": {
                "текила": "50 мл",
                "трипл сек": "20 мл",
                "лаймовый сок": "20 мл",
                "сахарный сироп": "10 мл",
                "лед": "кубики",
                "соль": "для ободка"
            },
            "recipe": "1. Обмакните край бокала в сок лайма и соль\n2. В шейкер со льдом добавьте все ингредиенты\n3. Взбейте и процедите в бокал\n4. Украсьте долькой лайма",
            "tags": ["классика", "текила", "цитрусовый", "соленый"],
            "strength": 25,
            "difficulty": "средне"
        },
        {
            "name": "Негрони",
            "description": "Итальянский аперитив с горьковатым вкусом",
            "ingredients": {
                "джин": "30 мл",
                "кампари": "30 мл",
                "красный вермут": "30 мл",
                "апельсин": "для украшения",
                "лед": "кубики"
            },
            "recipe": "1. Наполните бокал Old Fashioned льдом\n2. Добавьте все ингредиенты\n3. Аккуратно перемешайте барной ложкой\n4. Украсьте долькой апельсина",
            "tags": ["крепкий", "горький", "итальянский", "аперитив"],
            "strength": 28,
            "difficulty": "легко"
        }
    ]
    
    for cocktail_data in initial_cocktails:
        try:
            # Проверяем, не существует ли уже такой коктейль
            existing = await Database.get_cocktail_by_name(cocktail_data["name"])
            if existing:
                logger.info(f"Коктейль '{cocktail_data['name']}' уже существует, пропускаем")
                continue
                
            await Database.add_cocktail(**cocktail_data)
            logger.info(f"Добавлен: {cocktail_data['name']}")
        except Exception as e:
            logger.warning(f"Не удалось добавить {cocktail_data['name']}: {e}")

async def main():
    logger.info("=== ЗАПУСК COCKTAIL BOT ===")
    
    try:
        # Проверяем обязательные переменные
        if not config.BOT_TOKEN:
            logger.error("BOT_TOKEN не установлен!")
            logger.error("Добавьте BOT_TOKEN в .env файл или переменные окружения")
            return
        
        # Инициализация базы данных
        logger.info("1. Инициализация базы данных...")
        db_initialized = await initialize_database()
        if not db_initialized:
            logger.error("Не удалось инициализировать базу данных. Бот остановлен.")
            return
        
        # Инициализация Redis для FSM
        logger.info(f"2. Подключение к Redis: {config.REDIS_HOST}:{config.REDIS_PORT}")
        redis = Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            password=config.REDIS_PASSWORD,
            decode_responses=True
        )
        
        # Проверяем подключение к Redis
        try:
            await redis.ping()
            logger.info("✓ Redis подключен")
        except Exception as e:
            logger.error(f"✗ Ошибка подключения к Redis: {e}")
            logger.info("Использую memory storage (данные не сохранятся после перезапуска)")
            from aiogram.fsm.storage.memory import MemoryStorage
            storage = MemoryStorage()
        else:
            storage = RedisStorage(redis=redis)
        
        # Создаем бота и диспетчер
        logger.info("3. Создание бота и диспетчера...")
        bot = Bot(token=config.BOT_TOKEN)
        dp = Dispatcher(storage=storage)
        
        # Подключаем роутеры
        logger.info("4. Подключение обработчиков...")
        dp.include_router(admin_router)
        dp.include_router(user_router)
        
        # Запускаем бота
        if config.use_webhook:
            # Режим webhook для продакшена
            from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
            from aiohttp import web
            
            logger.info(f"5. Запуск в режиме webhook: {config.WEBHOOK_URL}")
            
            # Настраиваем webhook
            await bot.set_webhook(
                url=config.WEBHOOK_URL + config.WEBHOOK_PATH,
                drop_pending_updates=True
            )
            
            # Создаем aiohttp приложение
            app = web.Application()
            webhook_requests_handler = SimpleRequestHandler(
                dispatcher=dp,
                bot=bot,
            )
            
            webhook_requests_handler.register(app, path=config.WEBHOOK_PATH)
            setup_application(app, dp, bot=bot)
            
            # Добавляем health-check эндпоинт
            async def health_check(request):
                return web.Response(text="OK", status=200)
            
            app.router.add_get("/health", health_check)
            app.router.add_get("/", health_check)
            
            # Запускаем сервер
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host="0.0.0.0", port=config.PORT)
            await site.start()
            
            logger.info(f"✓ Сервер запущен на порту {config.PORT}")
            logger.info(f"✓ Health check: http://0.0.0.0:{config.PORT}/health")
            
            # Бесконечный цикл
            await asyncio.Event().wait()
            
        else:
            # Режим polling для разработки
            logger.info("5. Запуск в режиме polling (разработка)")
            await bot.delete_webhook()
            await dp.start_polling(bot)
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        sys.exit(1)
