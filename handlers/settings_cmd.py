import random

from aiogram import Router, types
from aiogram import F
from aiogram.filters import Command, BaseFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.users import clean_chat
from func.fsm import BattleState

rout = Router()


class IsAdmin(BaseFilter):  # [1]
    async def __call__(self, message: types.Message) -> bool:  # [3]
        if isinstance(message, types.CallbackQuery):
            member = await message.bot.get_chat_member(message.message.chat.id, message.from_user.id)
        else:
            member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        return (isinstance(member, types.ChatMemberAdministrator) and member.can_promote_members) or isinstance(member, types.ChatMemberOwner)




# class MyFilter(BoundFilter):
#     key = 'is_admin'
#
#     def __init__(self, is_admin):
#         self.is_admin = is_admin
#
#     async def check(self, message: types.Message):
#         member = await bot.get_chat_member(message.chat.id, message.from_user.id)
#         return member.is_chat_admin()


rout.message.filter(IsAdmin())
rout.callback_query.filter(IsAdmin())


class SettingsCallbackFactory(CallbackData, prefix="settings"):
    step: str
    value: str


class ClearTopCallback(CallbackData, prefix="clear_top"):
    answer: str



@rout.message(Command('settings'))
async def settings_battle(message: types.Message, state:FSMContext):
    text = "С битвами или без?"
    builder = InlineKeyboardBuilder()
    builder.button(
        text="С битвами(default)", callback_data=SettingsCallbackFactory(step='size', value='yes')
    )
    builder.button(
        text="Без", callback_data=SettingsCallbackFactory(step='size', value='no')
    )
    builder.adjust(2)
    await message.answer(text, reply_markup=builder.as_markup())


@rout.callback_query(SettingsCallbackFactory.filter(F.step == 'size'))
async def settings_size(callback: types.CallbackQuery, callback_data: SettingsCallbackFactory, state: FSMContext):
    if callback_data.value == "no":
        await state.set_state(BattleState.NO)
    else:
        await state.set_state(state=None)

    await state.update_data(battle=callback_data.value)
    text = "Размер сообщений(В разработке/не влияет):"
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Маленький", callback_data=SettingsCallbackFactory(step='end', value='small')
    )
    builder.button(
        text="Большой", callback_data=SettingsCallbackFactory(step='end', value='big')
    )
    builder.button(
        text="Адаптивный(default)", callback_data=SettingsCallbackFactory(step='end', value='adaptive')
    )
    builder.adjust(2)
    await callback.answer()
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@rout.callback_query(SettingsCallbackFactory.filter(F.step == 'end'))
async def settings_end(callback: types.CallbackQuery, callback_data: SettingsCallbackFactory, state: FSMContext):
    await state.update_data(size=callback_data.value)

    chat_settings = await state.get_data()
    text = f"Настройки сохранены:\nБитвы: {chat_settings['battle']}"

    await callback.answer()
    await callback.message.edit_text(text)


@rout.message(Command("clear_top"))
async def clear_top(message: types.Message):
    a = random.randint(0, 50)
    b = random.randint(a-9, a-1)
    answer = a - b
    builder = InlineKeyboardBuilder()
    for i in range(1, 10):
        if i == answer:
            builder.button(text=str(i), callback_data=ClearTopCallback(answer="1"))
        else:
            builder.button(text=str(i), callback_data=ClearTopCallback(answer="0"))

    builder.button(text="Отмена", callback_data=ClearTopCallback(answer="cancel"))
    builder.adjust(3)

    text=f"Сброс прогресса всех пользователей чата\n\n Для подтверждения ответьте на вопрос:\n<i>{a} - {b} = ?</i>"
    await message.reply(text=text, reply_markup=builder.as_markup())


@rout.callback_query(ClearTopCallback.filter())
async def success_clear(callback: types.CallbackQuery,callback_data: ClearTopCallback, session_maker):
    if callback.from_user.id != callback.message.reply_to_message.from_user.id:
        return await callback.answer("Не твоя кнопка, ты и не трогай", show_alert=True)

    if callback_data.answer == "cancel":
        text = "Отменено"
        await callback.answer()
        await callback.message.edit_text(text)

    elif callback_data.answer == "0":
        text = "Ошибка, попробуйте снова"
        await callback.answer()
        await callback.message.edit_text(text)

    else:
        await callback.answer()
        await callback.message.edit_text("*Сброс чата*")
        await clean_chat(callback.message.chat.id, session_maker=session_maker)
        text = "Сброс чата выполнен"
        await callback.message.edit_text(text)

