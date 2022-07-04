import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.types.bot_command_scope import (BotCommandScopeAllPrivateChats,
                                             BotCommandScopeChat)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config_loader import Config, load_config
from db.base import Base
from handlers.admin import admin_handlers
from handlers.bj_start import bj_start_handlers
from handlers.errors_handler import errors
from handlers.hit import hit_handlers
from handlers.stand import stand_handlers
from handlers.start import start_handlers
from middlewares.private_chat import CheckChatType
from middlewares.throttling import ThrottlingMiddleware


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Команда Start"),
        BotCommand(command="rules", description="Правила"),
        BotCommand(command="top", description="Топ игроков"),
        BotCommand(command="history", description="Профиль")
    ]
    admin_commands = [
        BotCommand(command="start", description="Команда Start"),
        BotCommand(command="rules", description="Правила"),
        BotCommand(command="top", description="Топ игроков"),
        BotCommand(command="history", description="Профиль"),
        BotCommand(command="admin", description="Админ меню")
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(746461090))
    await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(5131674802))


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        # filename="blackjack_logs.log"
    )

    config: Config = load_config()

    engine = create_async_engine(
        f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.db_name}",
        future=True
    )
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_sessionmaker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    storage = MemoryStorage()
    bot = Bot(config.bot.token, parse_mode="HTML")
    bot["db"] = async_sessionmaker
    dp = Dispatcher(bot, storage=storage)

    dp.middleware.setup(CheckChatType())
    dp.middleware.setup(ThrottlingMiddleware())

    errors(dp)
    start_handlers(dp)
    bj_start_handlers(dp)
    hit_handlers(dp)
    stand_handlers(dp)
    admin_handlers(dp)

    await set_bot_commands(bot)

    try:
        await dp.skip_updates()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    logging.error("Bot stopped!")
