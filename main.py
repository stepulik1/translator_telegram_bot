import asyncio
from aiogram import Bot, Dispatcher, types
from config import token
from app.database import async_main
from asyncio.exceptions import TimeoutError
from aiogram.exceptions import TelegramNetworkError

from app.favorites.interaction_favorites.deleting import router_deleting
from app.favorites.interaction_favorites.adding import router_adding
from app.translating.translating_queries import router_translating
from app.favorites.viewing.front_viewing import router_viewing
from app.test.testing_steps import router_testing_steps
from app.test.testing_queries import router_testing
from app.starting import router_start


bot = Bot(token=token)
dp = Dispatcher()


async def set_commands():
    commands_global = [
        types.BotCommand(command="add", description="Добавить слово в избранное"),
        types.BotCommand(command="del", description="Удалить запись из избранного"),
        types.BotCommand(command="words", description="Открыть избранное"),
        types.BotCommand(command="test", description="Учить слова"),
        types.BotCommand(command="end", description="Завершить тест предваритаельно"),
        types.BotCommand(command="s", description="Найти строку по id или слову"),
        types.BotCommand(command="mark", description="Пометить или убрать метку со строки")
    ]
    await bot.set_my_commands(commands_global, scope=types.BotCommandScopeDefault())



async def main():
    dp.include_routers(router_deleting, router_adding, router_viewing, router_start,
                       router_testing, router_testing_steps, router_translating)
    await set_commands()
    await async_main()
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except TimeoutError:
        print(f'error with timeuot')
    except TelegramNetworkError as e:
        print(e)

