import logging
from textwrap import dedent

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from custom_filters.filters import IsAdmin
from db.models import BJGame, Player
from keyboars import admin_kb, new_game_kb, user_page, user_page_kb
from middlewares.throttling import rate_limit
from sqlalchemy import select


async def admin_cmd(m: types.Message):
    await m.answer("🔞 Привет, Админ!", reply_markup=admin_kb)


async def back_to_admn(c: types.CallbackQuery):
    await c.message.edit_text("🔞 Привет, Админ!", reply_markup=admin_kb)
    await c.answer()


async def view_users(c: types.CallbackQuery):
    await c.answer()
    db = c.bot.get("db")

    async with db() as ssn:
        all_query = await ssn.execute(select(Player).order_by(Player.rating.desc()))
        all_p = all_query.scalars().all()
        await ssn.close()

    if len(all_p) == 0:
        await c.answer("⚠️ В базе данных нет игроков")

    else:
        last_page = len(all_p)
        page = 1

        usr = await c.bot.get_chat(all_p[0].plr_id)
        username = usr.username if usr.username else "???"

        text = f"""
        🆔 <b>UserID:</b> <i>{all_p[0].plr_id}</i>
        🆚 <b>UserName:</b> <i>@{username}</i>

        🔥 <b>Rating:</b> <i>{all_p[0].rating}</i>
        ♦️ <b>Games:</b> <i>{all_p[0].total_games}</i>
        """

        await c.message.edit_text(dedent(text), reply_markup=user_page_kb(page, last_page))


async def paginate_user(c: types.CallbackQuery, callback_data: dict):
    await c.answer()
    page = int(callback_data.get("page"))
    last_page = int(callback_data.get("last_page"))
    limit = 1
    db = c.bot.get("db")

    if page == 1:
        offset_ = limit
    else:
        offset_ = (page-1)*limit

    async with db() as ssn:
        all_query = await ssn.execute(select(Player).order_by(Player.rating.desc()).limit(1).offset(offset_))
        all_p = all_query.scalars().all()
        await ssn.close()

    usr = await c.bot.get_chat(all_p[0].plr_id)
    username = usr.username if usr.username else "???"

    text = f"""
        🆔 <b>UserID:</b> <i>{all_p[0].plr_id}</i>
        🆚 <b>UserName:</b> <i>@{username}</i>

        🔥 <b>Rating:</b> <i>{all_p[0].rating}</i>
        ♦️ <b>Games:</b> <i>{all_p[0].total_games}</i>
        """

    await c.message.edit_text(dedent(text), reply_markup=user_page_kb(page, last_page))


async def useless_btn(c: types.CallbackQuery):
    await c.answer()


def admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_cmd, IsAdmin(), commands="admin")
    dp.register_callback_query_handler(back_to_admn, text="back_to_admin")
    dp.register_callback_query_handler(
        view_users, IsAdmin(), text="view_all_players")
    dp.register_callback_query_handler(paginate_user, user_page.filter())
    dp.register_callback_query_handler(
        useless_btn, Text(startswith="uselessbtn_"))
