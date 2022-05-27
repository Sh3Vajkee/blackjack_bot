import logging
from textwrap import dedent

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from db.models import BJGame
from keyboars import new_game_kb
from middlewares.throttling import rate_limit
from sqlalchemy.orm import selectinload
from utils.points_count import hit_count_points


@rate_limit(0.5)
async def bj_stand(c: types.CallbackQuery):
    await c.answer(cache_time=1)
    db = c.bot.get("db")

    game_id = int(c.data.split("_")[-1])

    async with db() as ssn:

        game: BJGame = await ssn.get(BJGame, game_id, options=[selectinload(BJGame.player)])

        if game is None:
            await ssn.close()
            await c.message.answer("⚠️ Game Not Found")
            return

        dealer_points = game.d_points
        dealer_cards = game.d_cards
        count = 0
        next_cards = game.next_cards.split("_")

        while dealer_points < 17:
            new_d_points = await hit_count_points(dealer_points, next_cards[count])
            dealer_points = new_d_points
            dealer_cards += f"_{next_cards[count]}"
            count += 1

        d_cards_txt = "   •    ".join(
            d_card for d_card in dealer_cards.split("_"))
        p_cards_txt = "   •    ".join(
            p_card for p_card in game.p_cards.split("_"))

        game.d_points = dealer_points
        game.d_cards = dealer_cards

        if (dealer_points > 21) or (dealer_points < game.p_points):
            game.result = "player_win"
            game.player.rating += game.bet_amount

            answer_txt = f"""
            🥳 <b>Вы выиграли!</b>

            [ ♦️ Стол № {game_id} ]

            Дилер ({dealer_points})
            {d_cards_txt}

            Игрок ({game.p_points})
            {p_cards_txt}

            🔥 Рейтинг: {game.player.rating}      ⬆️<i>(+{game.bet_amount})</i>
            """
            logging.info(
                f"Game {game_id}|Dealer {dealer_cards}({dealer_points})|Player {game.p_cards}({game.p_points})|player_win 10")

        elif dealer_points == game.p_points:
            game.result = "tie"

            answer_txt = f"""
            🤝 <b>Ничья!</b>

            [ ♦️ Стол № {game_id} ]

            Дилер ({dealer_points})
            {d_cards_txt}

            Игрок ({game.p_points})
            {p_cards_txt}

            🔥 Рейтинг: {game.player.rating}
            """
            logging.info(
                f"Game {game_id}|Dealer {dealer_cards}({dealer_points})|Player {game.p_cards}({game.p_points})|tie")

        else:
            game.result = "player_lose"
            game.player.rating -= game.bet_amount

            answer_txt = f"""
            🥺 <b>Вы проиграли!</b>

            [ ♦️ Стол № {game_id} ]

            Дилер ({dealer_points})
            {d_cards_txt}

            Игрок ({game.p_points})
            {p_cards_txt}

            🔥 Рейтинг: {game.player.rating}      🔻<i>(-{game.bet_amount})</i>
            """
            logging.info(
                f"Game {game_id}|Dealer {dealer_cards}({dealer_points})|Player {game.p_cards}({game.p_points})|player_lose 10")

        await ssn.commit()
        await ssn.close()

    await c.message.edit_text(dedent(answer_txt), reply_markup=new_game_kb)


def stand_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(bj_stand, Text(startswith="stand_"))
