from aiogram import types

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
