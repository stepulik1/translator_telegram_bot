from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from config import token
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
import app.test.back_testing as back_testing
import app.test.testing_steps as testing_steps

router_testing = Router()
bot = Bot(token=token)


@router_testing.message(Command('end'))
async def ending_test(message: Message, state: FSMContext):
    state_data = await state.get_data()

    if not state_data:
        await message.answer(text='<b>Вам нечего завершать!</b>\n\n'
                                  '<i>Чтобы начать тест, нажмите</i> /test', parse_mode='html')
        return

    text = '<i>Ваш тест завершен!</i>'

    try:
        final_accuracy = state_data["final_accuracy"]
        step = state_data["step"]

        if step != 0:
            final_accuracy = round(round(final_accuracy / (step * 100), 3) * 100, 1)
            text += f'\n\nИз {step} вопросов ваша точность совпадений составила <b>{final_accuracy} %</b>!'

        if not state_data["available_test"]:
            message_id = state_data["message_id"]
            await bot.edit_message_text(text=text, message_id=message_id,
                                        chat_id=message.chat.id, parse_mode='html')
        else:
            raise KeyError

    except KeyError:
        await message.answer(text=text, parse_mode='html')

    await state.clear()



@router_testing.message(Command('test'))
async def test_head(message: Message, state: FSMContext):
    await message.answer(text='<b>Сколько слов вы хотите проверить?</b>\n\n'
                              'Чтобы проверить все слова, введите <b>"Все"</b>', parse_mode='html')
    await state.clear()
    await state.update_data(available_test=True)
    await state.set_state(testing_steps.test_steps.preparation)



@router_testing.callback_query(F.data.startswith('test'))
async def pre_process_test(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    message_id = callback.message.message_id

    if not state_data:
        await callback.answer(text='Этот тест не доступен!', show_alert=True)
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=message_id)
        return

    if len(state_data) > 1:
        delete_messages = state_data["delete_message"]
        for delete in delete_messages:
            await bot.delete_message(chat_id=callback.message.chat.id,
                                     message_id=delete)
        step = state_data["step"] - len(delete_messages) + 1
        await state.update_data(step=step, delete_message=[])

    else:
        callback_data = callback.data.split('_')
        count = int(callback_data[1])
        lang = int(callback_data[2])
        words = await back_testing.get_test_words(callback.from_user.id, lang, count)
        await state.update_data(count=count, step=0, message_id=message_id, delete_message=[],
                                words=words, restriction={}, final_accuracy=0)
        delete = 1
        while True:
            try:
                await bot.delete_message(chat_id=callback.message.chat.id,
                                         message_id=message_id + delete)
                delete += 1
            except TelegramBadRequest:
                break

    await testing_steps.process_test(callback.message, state)

