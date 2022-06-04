import logging
from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsAdmin(BoundFilter):
    key = 'is_admin'

    async def check(self, target: Union[types.Message, types.CallbackQuery]):
        admins = [746461090, 5131674802]

        usr_id = target.from_user.id if isinstance(
            target, types.CallbackQuery) else target.from_user.id

        return usr_id in admins
