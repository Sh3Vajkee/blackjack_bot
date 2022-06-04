from aiogram import types
from aiogram.utils.callback_data import CallbackData

new_game_kb = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(
                "♦️ Новая игра ♣️", callback_data="new_game")
        ]
    ]
)


def get_bj_kb(game_id):

    bjgame_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    "🃏 Еще", callback_data=f"hit_{game_id}"),
                types.InlineKeyboardButton(
                    "✋ Хватит", callback_data=f"stand_{game_id}"),
            ]
        ]
    )
    return bjgame_kb


admin_kb = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(
                "Просмотр всех игроков", callback_data="view_all_players")
        ]
    ]
)


user_page = CallbackData("pages", "page", "last_page")


def user_page_kb(page, last_page):

    page_btns = []
    if page == 2:
        page_btns.append(types.InlineKeyboardButton(
            "⬅️", callback_data="view_all_players"))

    elif page > 1:
        page_btns.append(types.InlineKeyboardButton(
            "⬅️", callback_data=user_page.new(page=page-1, last_page=last_page)))

    page_btns.append(types.InlineKeyboardButton(
        f"({page}/{last_page})", callback_data=f"uselessbtn_{page}"))

    if page < last_page:
        page_btns.append(types.InlineKeyboardButton(
            "➡️", callback_data=user_page.new(page=page+1, last_page=last_page)))

    back_btn = [types.InlineKeyboardButton(
        "🔙", callback_data="back_to_admin")]

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[page_btns, back_btn])

    return keyboard
