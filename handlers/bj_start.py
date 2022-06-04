import asyncio
import logging
import random
from textwrap import dedent

from aiogram import Dispatcher, types
from db.models import BJGame, Player
from keyboars import get_bj_kb, new_game_kb
from middlewares.throttling import rate_limit
from sqlalchemy import update
from utils.points_count import first_count_points


@rate_limit(1)
async def new_game(c: types.CallbackQuery):
    await c.answer()
    await c.message.edit_reply_markup()

    db = c.bot.get("db")

    bet_amount = 10
    deck = ['2♣️', '3♣️', '4♣️', '5♣️', '6♣️', '7♣️', '8♣️', '9♣️', '10♣️', 'J♣️', 'Q♣️', 'K♣️', 'A♣️',
            '2♦️', '3♦️', '4♦️', '5♦️', '6♦️', '7♦️', '8♦️', '9♦️', '10♦️', 'J♦️', 'Q♦️', 'K♦️', 'A♦️',
            '2♥️', '3♥️', '4♥️', '5♥️', '6♥️', '7♥️', '8♥️', '9♥️', '10♥️', 'J♥️', 'Q♥️', 'K♥️', 'A♥️',
            '2♠️', '3♠️', '4♠️', '5♠️', '6♠️', '7♠️', '8♠️', '9♠️', '10♠️', 'J♠️', 'Q♠️', 'K♠️', 'A♠️']

    msg = await c.message.answer("💬 Раздаю карты...")
    await asyncio.sleep(.5)

    while True:
        selected_cards = random.choices(deck, k=14)
        if len(selected_cards) == len(set(selected_cards)):
            break

    next_cards = "_".join([card for card in selected_cards[4:]])

    dealer_cards = [selected_cards[0], selected_cards[2]]
    dealer_points = await first_count_points(dealer_cards)

    player_cards = [selected_cards[1], selected_cards[3]]
    player_points = await first_count_points(player_cards)

    async with db() as ssn:
        player: Player = await ssn.get(Player, c.from_user.id)
        player.total_games += 1

        if (player_points >= 21 and dealer_points < 21) or (player_points == 21 and dealer_points == 22):
            game = await ssn.merge(BJGame(
                game_id=msg.message_id,
                bet_amount=bet_amount,
                result="player_win",
                d_cards=f"{selected_cards[0]}_{selected_cards[2]}",
                d_points=dealer_points,
                p_id=c.from_user.id,
                p_cards=f"{selected_cards[1]}_{selected_cards[3]}",
                p_points=player_points
            ))
            # await ssn.execute(update(Player).filter(Player.plr_id == c.from_user.id).values(
            #     rating=Player.rating+bet_amount, total_games=Player.total_games+1))
            player.rating += int(bet_amount * 1.5)

            await ssn.commit()

            answer_text = f"""
            🥳 <b>Вы выиграли!</b>
            У Вас <b>BlackJack</b>!

            [ ♦️ Стол № {msg.message_id} ]

            Дилер ({dealer_points})
            {selected_cards[0]}   •    {selected_cards[2]}

            Игрок ({player_points})
            {selected_cards[1]}   •    {selected_cards[3]}

            
            🔥 Рейтинг: {player.rating}      ⬆️<i>(+{int(bet_amount*1.5)})</i>
            """

            await c.message.answer(dedent(answer_text), reply_markup=new_game_kb)
            logging.info(
                f"Game {msg.message_id}|{c.from_user.id}|Dealer {selected_cards[0]}_{selected_cards[2]}({dealer_points})|Player {selected_cards[1]}_{selected_cards[3]}({player_points})|player_win 15")

        elif (player_points == dealer_points == 21) or (player_points == dealer_points == 22):
            game = await ssn.merge(BJGame(
                game_id=msg.message_id,
                bet_amount=bet_amount,
                result="tie",
                d_cards=f"{selected_cards[0]}_{selected_cards[2]}",
                d_points=dealer_points,
                p_id=c.from_user.id,
                p_cards=f"{selected_cards[1]}_{selected_cards[3]}",
                p_points=player_points
            ))
            # await ssn.execute(update(Player).filter(Player.plr_id == c.from_user.id).values(
            #     total_games=Player.total_games+1))

            await ssn.commit()

            answer_text = f"""
            🤝 <b>Ничья!</b>
            <b>BlackJack</b> vs <b>BlackJack</b>

            [ ♦️ Стол № {msg.message_id} ]

            Дилер ({dealer_points})
            {selected_cards[0]}   •    {selected_cards[2]}

            Игрок ({player_points})
            {selected_cards[1]}   •    {selected_cards[3]}

            🔥 Рейтинг: {player.rating}
            """
            await c.message.answer(dedent(answer_text), reply_markup=new_game_kb)
            logging.info(
                f"Game {msg.message_id}|{c.from_user.id}|Dealer {selected_cards[0]}_{selected_cards[2]}({dealer_points})|Player {selected_cards[1]}_{selected_cards[3]}({player_points})|tie")

        elif (dealer_points >= 21 and player_points < 21) or (dealer_points == 21 and player_points == 22):
            game = await ssn.merge(BJGame(
                game_id=msg.message_id,
                bet_amount=bet_amount,
                result="player_lose",
                d_cards=f"{selected_cards[0]}_{selected_cards[2]}",
                d_points=dealer_points,
                p_id=c.from_user.id,
                p_cards=f"{selected_cards[1]}_{selected_cards[3]}",
                p_points=player_points
            ))
            # await ssn.execute(update(Player).filter(Player.plr_id == c.from_user.id).values(
            #     rating=Player.rating-bet_amount, total_games=Player.total_games+1))
            player.rating -= bet_amount
            await ssn.commit()
            await ssn.close()

            answer_text = f"""
            🥺 <b>Вы проиграли!</b>
            У Дилера <b>BlackJack</b>!

            [ ♦️ Стол № {msg.message_id} ]

            Дилер ({dealer_points})
            {selected_cards[0]}   •    {selected_cards[2]}

            Игрок ({player_points})
            {selected_cards[1]}   •    {selected_cards[3]}

            🔥 Рейтинг: {player.rating}      🔻<i>(-{bet_amount})</i>
            """

            await c.message.answer(dedent(answer_text), reply_markup=new_game_kb)
            logging.info(
                f"Game {msg.message_id}|{c.from_user.id}|Dealer {selected_cards[0]}_{selected_cards[2]}({dealer_points})|Player {selected_cards[1]}_{selected_cards[3]}({player_points})|player_lose 10")

        else:
            game = await ssn.merge(BJGame(
                game_id=msg.message_id,
                bet_amount=bet_amount,
                next_cards=next_cards,
                d_cards=f"{selected_cards[0]}_{selected_cards[2]}",
                d_points=dealer_points,
                p_id=c.from_user.id,
                p_cards=f"{selected_cards[1]}_{selected_cards[3]}",
                p_points=player_points
            ))
            await ssn.commit()
            await ssn.close()

            answer_text = f"""
            [ ♦️ Стол № {msg.message_id} ]

            Дилер (❔)
            {selected_cards[0]}   •    [❔]

            Игрок ({player_points})
            {selected_cards[1]}   •    {selected_cards[3]}

            Выберите действие⬇️
            """

            await c.message.answer(dedent(answer_text), reply_markup=get_bj_kb(msg.message_id))


def bj_start_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(new_game, text="new_game")
