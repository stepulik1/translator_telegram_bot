from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
import app.test.back_testing as back_test
import app.keyboard as keyboard
import app.favorites.viewing.back_viewing as back_viewing
import app.test.testing_queries as testing_queries
import app
router_testing_steps = Router()

class test_steps(StatesGroup):
    preparation = State()
    do_nothing = State()
    answer = State()
    excess_message = State()


@router_testing_steps.message(test_steps.preparation)
async def test_preparation(message: Message, state: FSMContext):
    text = message.text
    tg_id = message.from_user.id
    words_count = await back_viewing.view_favorites(tg_id, page=None, words_count=True)

    try:
        count = int(text)
        if count < 0 or text[0] == '0':
            raise ValueError

    except ValueError:
        if text.lower().strip() != 'все':
            await message.answer(text='Вы написали что-то не то! <b>Введите положительное число.</b> ❌',
                                 parse_mode='html')
            return
        count = words_count

    if words_count < 1:
        await message.answer(text='В вашем избранном <b>нету слов!</b> ❌', parse_mode='html')
        return

    if count > words_count:
        await message.answer(text='В вашем избранном <b>нету столько слов!</b> ❌', parse_mode='html')
        return

    await message.answer(text='<b>Какие слова вы хотите проверить?</b>', parse_mode='html',
                         reply_markup=await keyboard.test(count, None))
    await state.set_state(test_steps.do_nothing)



@router_testing_steps.message(test_steps.do_nothing)
async def do_nothing_test(message: Message):
    try:
        await message.reply(text='Для того что-бы закончить тест используйте /end')
    except TelegramBadRequest:
        await message.delete()



async def process_test(message: Message, state: FSMContext):
    if await back_test.in_process_test(message, state):
        await testing_queries.ending_test(message, state)
        return

    await state.set_state(test_steps.answer)



@router_testing_steps.message(test_steps.answer)
async def answer_test(message: Message, state: FSMContext):
    if await back_test.in_answer_test(message, state):
        await testing_queries.ending_test(message, state)
        return

    await state.set_state(test_steps.excess_message)



@router_testing_steps.message(test_steps.excess_message)
async def excess(message: Message, state: FSMContext):
    await message.delete()
    await state.set_state(test_steps.excess_message)
