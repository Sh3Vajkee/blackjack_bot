from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


class CheckChatType(BaseMiddleware):

    async def on_pre_process_update(self, u: types.Update, data: dict):

        if u.message:
            ch_type = u.message.chat.type
        elif u.callback_query:
            ch_type = u.callback_query.message.chat.type
        else:
            return

        if ch_type != "private":
            raise CancelHandler()
