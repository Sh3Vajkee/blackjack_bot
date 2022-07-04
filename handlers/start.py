import datetime as dt
import logging
from textwrap import dedent

import pytz
from aiogram import Dispatcher, types
from db.models import BJGame, Player
from keyboars import new_game_kb
from middlewares.throttling import rate_limit
from sqlalchemy import select


@rate_limit(1)
async def start_cmd(m: types.Message):
    text = """
    👋 Добро пожаловать в <b>BlackJackBot</b>!
    
    /rules - 📋 правила
    /top - 🏆 топ игроков
    /history - 👤 профиль
    /donate - поддержать проект

    ℹ️ <i>По всем вопросам писать @Tshque</i>
    """
    await m.answer(dedent(text), reply_markup=new_game_kb)

    db = m.bot.get("db")

    async with db() as ssn:
        plr = await ssn.get(Player, m.from_user.id)
        if not plr:
            date = int(dt.datetime.now(
                pytz.timezone("Europe/Moscow")).timestamp())
            await ssn.merge(Player(plr_id=m.from_user.id, join_date=date, last_activity=date))
            await ssn.commit()
            logging.info(f"New Player with ID: {m.from_user.id}")
        await ssn.close()


@rate_limit(1)
async def rules_cmd(m: types.Message):
    db = m.bot.get("db")

    async with db() as ssn:
        plr = await ssn.get(Player, m.from_user.id)
        if not plr:
            await ssn.merge(Player(plr_id=m.from_user.id))
            await ssn.commit()
            logging.info(f"New Player with ID: {m.from_user.id}")
        await ssn.close()

    text = """
    📋 Правила игры в BlackJack

    В игре небходимо набрать <b>21 очко</b>.

    Дилер раздает две карты игроку и две себе, одну из них взакрытую. 
    Если первые две карты у игрока дадут в сумме 21 очков, то он автоматически побеждает и получает 15 очков рейтинга,
    но только если у дилера тоже нет 21 очка с первых двух карт. Если же у дилера 21 очков с раздачи,
    а у игрока нет, то игрок автоматическипроигрывает 10 очков рейтинга.

    Если же из первых двух карт выпадет два туза (AA), то эта комбинация дает 22 очка. Тот, у кого выпала эта комбинация
    на старте автатически выигрывает если:
        - <u>у оппонента не 22 очка</u> (в этом случае будет ничья)
        - <u>у оппонента не 21 очка</u> (в этом случае тот, у кого 22 очка проигрывает, так как эта комбинация выше по старшинству)
    
    Если же на старте никому не выпадает 21 или 22 очка, то игрок решает, что ему делать: добирать еще карту, или оставить как есть.
    Если после добора сумма очков будет больше 21, то игрок автоматически проигрывает.
    Если после добора сумма очков будет равна 21, то добирать больше нельзя и смотрят карты у дилера, и если там будет 21, то ничья,
    а если меньше или перебор, то игрок побеждает и получает 10 очков рейтинга

    Стоимость карт:
    <i>2, 3, 4, 5, 6, 7, 8, 9, 10</i> - дают тоже количество очков, что и цифра на карте
    <i>J, Q, K</i> - дают 10 очков
    <i>A</i> - дает 1 или 11 очков:
        - <u>11 очков</u> - при раздаче карт, или если после добора туза (А) нет перебора
        - <u>1 очко</u> - когда после добора туза (А) игрок получает перебор
    
    ♦️ Приступить к игре - нажмите   /start


    ℹ️ <i>По всем вопросам писать @Tshque</i>
    """
    await m.answer(dedent(text))


@rate_limit(1)
async def top_cmd(m: types.Message):
    db = m.bot.get("db")

    async with db() as ssn:
        plr = await ssn.get(Player, m.from_user.id)
        if not plr:
            await ssn.merge(Player(plr_id=m.from_user.id))
            await ssn.commit()
            logging.info(f"New Player with ID: {m.from_user.id}")

        top_q = await ssn.execute(select(Player).order_by(Player.rating.desc()))
        top = top_q.scalars().all()
        await ssn.close()

    medal = ["🥇", "🥈", "🥉", "🔹", "🔹", "🃏"]
    players = []
    count = 1
    for plr in top:
        if plr.plr_id == m.from_user.id:
            plr_place = count
            plr_points = plr.rating
            if count <= 5:
                plr_medal = medal[count-1]
            else:
                plr_medal = medal[-1]
        if count <= 5:
            players.append(
                f"{medal[count-1]} {count}. ID:{plr.plr_id} - <b>{plr.rating}</b>")

        count += 1

    txt = "🏆 <b>Топ игроков:</b>\n\n" + \
        "\n".join(
            players) + f"\n\n<b>. . .</b>\n\n{plr_medal} {plr_place}. Ваш рейтинг - <b>{plr_points}</b>\n\n\nℹ️ <i>По всем вопросам писать @Tshque</i>\n/donate - поддержать проект"

    await m.answer(txt, reply_markup=new_game_kb)


@rate_limit(1)
async def games_history(m: types.Message):
    db = m.bot.get("db")

    async with db() as ssn:
        plr = await ssn.get(Player, m.from_user.id)
        if not plr:
            await ssn.merge(Player(plr_id=m.from_user.id))
            await ssn.commit()
            logging.info(f"New Player with ID: {m.from_user.id}")
            plr_rating = 1000
            plr_total_games = 0

        else:
            plr_rating = plr.rating
            plr_total_games = plr.total_games

        games_query = await ssn.execute(select(BJGame).order_by(BJGame.game_id.desc()).filter(
            BJGame.player.has(Player.plr_id == m.from_user.id)).limit(10))
        games = games_query.scalars().all()

        plr = await ssn.get(Player, m.from_user.id)
        plr_rating = plr.rating
        plr_total_games = plr.total_games
        await ssn.close()

    if len(games) > 0:
        game_txts = []
        for game in games:

            if game.result == "player_win":
                ico = "🟢 WIN   - "
            elif game.result == "player_lose":
                ico = "🔴 LOSE - "
            elif game.result == "tie":
                ico = "⚪ TIE     - "
            else:
                ico = "❔ OPEN - "

            game_txts.append(f"{ico} Стол №<u>{game.game_id}</u> ")

        header_txt = f"👤 Ваши результаты\n\n🔥 Рейтинг: {plr_rating}\n♦️ Всего игр: {plr_total_games}\n\n"
        txt = "📋 Последние игры:\n\n" + \
            "\n".join(game_txt for game_txt in game_txts)

    else:
        txt = "🥺 Вы еще не сыграли ниодной игры"

    await m.answer(header_txt + txt + "\n\n\nℹ️ <i>По всем вопросам писать @Tshque</i>\n/donate - поддержать проект",
                   reply_markup=new_game_kb)


@rate_limit(1)
async def supp_project(m: types.Message):
    txt = f"""
    👍 Поддержи проект!

    BTC:
    <code>1N9vLNJUmdmrpQtL8u1h8u5L7hkRvLWuSk</code>

    ETH:
    <code>2e7b75c52bacd1493ffc454c13630d5858274b59</code>
    
    LTC:
    <code>Lh9gaup7WqnVUcRhDrjxQMsKmb2C2kHQ6D</code>

    DOGE:
    <code>DT2QTDbdM8kGQdLuSgur3ZYaMqW9ScozzL</code>

    DASH:
    <code>Xsu56hf48HKYP3m3PPJfGNkPZmYCHwEiJJ</code>
    """

    await m.answer(dedent(txt))


def start_handlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands="start")
    dp.register_message_handler(rules_cmd, commands="rules")
    dp.register_message_handler(top_cmd, commands="top")
    dp.register_message_handler(games_history, commands="history")
    dp.register_message_handler(supp_project, commands="donate")
