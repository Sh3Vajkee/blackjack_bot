import logging
from textwrap import dedent

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from db.models import BJGame
from keyboars import get_bj_kb, new_game_kb
from middlewares.throttling import rate_limit
from sqlalchemy.orm import selectinload
from utils.points_count import hit_count_points, player_hit


@rate_limit(0.5)
async def bj_hit(c: types.CallbackQuery):
    await c.answer(cache_time=1)

    db = c.bot.get("db")

    game_id = int(c.data.split("_")[-1])

    async with db() as ssn:

        game: BJGame = await ssn.get(BJGame, game_id, options=[selectinload(BJGame.player)])

        if game is None:
            await ssn.close()
            await c.message.answer("⚠️ Game Not Found")
            return

        plr_hit_res = await player_hit(game.p_points, game.p_cards, game.next_cards)

        p_cards_txt = "   •    ".join(
            card for card in plr_hit_res[1].split("_"))

        game.next_cards = plr_hit_res[2]
        game.p_points = plr_hit_res[0]
        game.p_cards = plr_hit_res[1]

        if plr_hit_res[0] > 21:
            game.result = "player_lose"
            game.player.rating -= game.bet_amount

            await ssn.commit()

            answer_txt = f"""
            🥺 <b>Вы проиграли!</b>

            [ ♦️ Стол № {game_id} ]

            Дилер ({game.d_points})
            {game.d_cards.split("_")[0]}   •    {game.d_cards.split("_")[1]}

            Игрок ({plr_hit_res[0]})
            {p_cards_txt}

            🔥 Рейтинг: {game.player.rating}      🔻<i>(-{game.bet_amount})</i>
            """

            await c.message.edit_text(dedent(answer_txt), reply_markup=new_game_kb)
            logging.info(
                f"Game {game_id}|{c.from_user.id}|Dealer {game.d_cards}({game.d_points})|Player {plr_hit_res[1]}({plr_hit_res[0]})|player_lose 10")

        elif plr_hit_res[0] == 21:

            dealer_points = game.d_points
            dealer_cards = game.d_cards
            count = 0
            next_cards = plr_hit_res[2].split("_")

            while dealer_points < 17:
                new_d_points = await hit_count_points(dealer_points, next_cards[count])
                dealer_points = new_d_points
                dealer_cards += f"_{next_cards[count]}"
                count += 1

            d_cards_txt = "   •    ".join(
                d_card for d_card in dealer_cards.split("_"))
            game.d_points = dealer_points
            game.d_cards = dealer_cards

            if dealer_points != 21:
                game.result = "player_win"
                game.player.rating += game.bet_amount
                await ssn.commit()

                answer_txt = f"""
                🥳 <b>Вы выиграли!</b>

                [ ♦️ Стол № {game_id} ]

                Дилер ({dealer_points})
                {d_cards_txt}

                Игрок ({plr_hit_res[0]})
                {p_cards_txt}

                🔥 Рейтинг: {game.player.rating}      ⬆️<i>(+{game.bet_amount})</i>
                """

                await c.message.edit_text(dedent(answer_txt), reply_markup=new_game_kb)
                logging.info(
                    f"Game {game_id}|{c.from_user.id}|Dealer {dealer_cards}({dealer_points})|Player {plr_hit_res[1]}({plr_hit_res[0]})|player_win 10")

            else:
                game.result = "tie"
                await ssn.commit()

                answer_txt = f"""
               🤝 <b>Ничья!</b>

                [ ♦️ Стол № {game_id} ]

                Дилер ({dealer_points})
                {d_cards_txt}

                Игрок ({plr_hit_res[0]})
                {p_cards_txt}

                🔥 Рейтинг: {game.player.rating}
                """

                await c.message.edit_text(dedent(answer_txt), reply_markup=new_game_kb)
                logging.info(
                    f"Game {game_id}|{c.from_user.id}|Dealer {dealer_cards}({dealer_points})|Player {plr_hit_res[1]}({plr_hit_res[0]})|Tie")

        else:
            answer_txt = f"""
            [ ♦️ Стол № {game_id} ]

            Дилер (❔)
            {game.d_cards.split("_")[0]}   •    [❔]

            Игрок ({plr_hit_res[0]})
            {p_cards_txt}

            Выберите действие⬇️
            """

            await c.message.edit_text(dedent(answer_txt), reply_markup=get_bj_kb(game.game_id))

        await ssn.commit()
        await ssn.close()


def hit_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(bj_hit, Text(startswith="hit_"))
