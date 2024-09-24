from aiogram.types import Message
from aiogram import Router
from aiogram.filters import CommandObject, Command
from aiogram.fsm.context import FSMContext
import app.favorites.managing_favorites as managing_favorites
import app.additional.spelling as spelling
import app.additional.massive as massive
import app.favorites.viewing.back_viewing as back_viewing

router_deleting = Router()


@router_deleting.message(Command('del'))
async def delete_word(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    args = command.args
    tg_id = message.from_user.id
    words_count = await back_viewing.view_favorites(tg_id, None, True)

    if words_count == 0:
        await message.answer(text='<b>У вас пока нету избранного! Добавьте хотя-бы один элемент</b> 🌟',
                             parse_mode='html')
        return

    number = await massive.check_valid_number(args, words_count, message)

    if not number:
        return

    try:
        first_number = number[0]
        second_number = number[1] + 1
        head = f'<b>Строки с айди <code>"{first_number} - {second_number - 1}"</code> удалены!</b> 🍀\n\n'

    except TypeError:
        first_number = number
        second_number = first_number + 1
        head = f'<b>Строка с айди <code>"{first_number}"</code> удалена!</b> 🍀\n\n'

    reps = second_number - first_number
    index = 0
    answer = ''

    for _ in range(reps):
        if index < 3:
            en_word, ru_word = await managing_favorites.managing_indexes(tg_id, first_number, delete=False)
            marking_data = await spelling.define_mark(en_word, ru_word, '')
            en_word, ru_word, mark_presence = marking_data[0], marking_data[1], marking_data[2]
            if mark_presence == spelling.mark:
                en_word = f'<b>{en_word}</b>'

            answer += (f'{mark_presence}<b>{first_number + index}</b>.  {en_word}  '
                       f'<b>—</b>  <code>{ru_word}</code>\n\n')
        elif index == 3:
            answer += '<b>· · ·</b>'

        await managing_favorites.managing_indexes(tg_id, first_number, delete=True)
        index += 1

    await message.answer(text=head + answer, parse_mode='html')
