import logging

from aiogram import Dispatcher
from aiogram.utils.exceptions import (BadRequest, CantParseEntities,
                                      InvalidQueryID, MessageCantBeDeleted,
                                      MessageCantBeEdited, MessageNotModified,
                                      MessageTextIsEmpty,
                                      MessageToDeleteNotFound,
                                      MessageToEditNotFound, RetryAfter,
                                      TelegramAPIError, Unauthorized)


async def errors_handler(update, exception):

    if isinstance(exception, MessageNotModified):
        logging.error(f"Message Not Modified: {exception}\nUpdate: {update}")
        return True

    if isinstance(exception, MessageCantBeDeleted):
        logging.error(f"MessageCantBeDeleted: {exception}\nUpdate: {update}")
        return True

    if isinstance(exception, MessageToDeleteNotFound):
        logging.error(
            f"MessageToDeleteNotFound: {exception}\nUpdate: {update}")
        return True

    if isinstance(exception, MessageCantBeEdited):
        logging.error(f"MessageCantBeEdited: {exception}\nUpdate: {update}")
        return True

    if isinstance(exception, MessageToEditNotFound):
        logging.error(f"MessageToEditNotFound: {exception}\nUpdate: {update}")
        return True

    if isinstance(exception, MessageTextIsEmpty):
        logging.error(f"MessageTextIsEmpty: {exception}\nUpdate: {update}")
        return True

    if isinstance(exception, Unauthorized):
        logging.error(f"Unauthorized: {exception}")
        return True

    if isinstance(exception, InvalidQueryID):
        logging.error(f"InvalidQueryId: {exception}\nUpdate: {update}")
        return True

    if isinstance(exception, CantParseEntities):
        logging.error(f"CantParseEntities: {exception}\nUpdate: {update}")
        return True

    if isinstance(exception, RetryAfter):
        print("124")
        logging.error(f"RetryAfter: {exception}\nUpdate: {update}")
        return True

    if isinstance(exception, BadRequest):
        logging.error(f"BadRequest: {exception}\nUpdate: {update}")
        return True

    if isinstance(exception, TelegramAPIError):
        logging.error(f"TelegrapAPIError: {exception}\nUpdate: {update}")
        return True

    logging.error(f"Update: {update}\n{exception}")


def errors(dp: Dispatcher):
    dp.register_errors_handler(errors_handler)
