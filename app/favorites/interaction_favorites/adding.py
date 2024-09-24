from aiogram.types import Message, CallbackQuery
from aiogram import Router, F, Bot
from config import token
from aiogram.filters import CommandObject, Command
import app.additional.spelling as spelling
import app.favorites.managing_favorites as managing_favorites
import app.favorites.viewing.back_viewing as back_viewing
from aiogram.fsm.context import FSMContext
import app.keyboard as keyboard
router_adding = Router()
bot = Bot(token=token)


@router_adding.message(Command('add'))
async def add_word(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    tg_id = message.from_user.id
    added_words = await managing_favorites.add_words_list(tg_id, words_to_add=None, is_add=False)

    if not added_words:
        await message.answer(text='<b>Вам нечего добавлять в избранное!</b> 🙄', parse_mode='html')
        return

    added_words = added_words.split(spelling.separate)
    word_to_add = command.args

    if not word_to_add:
        word_to_add = added_words[1]

    if len(word_to_add) > 30:
        await message.answer(text='<b>Слишком длинный текст!</b>', parse_mode='html')
        return

    if word_to_add.capitalize() not in added_words[1:]:
        await message.answer(text=f'<b>"{word_to_add}"</b> нету в текущем переводе! ❌',
                             parse_mode='html')
    else:
        origin = added_words[0]
        en_word, ru_word = await spelling.define_lang(origin, None, None)

        index = await back_viewing.check_word(tg_id, en_word, ru_word, None)
        if index:
            await message.answer(text=f'Сущетсвует идентичная запись в вашем избранном!\n\n'
                                 f'<b>{index}.</b>  {origin}  <b>—</b>  <code>{word_to_add}</code>'
                                 '\n\n<b>Вы уверены что хотите добавить этот перевод?</b>', parse_mode='html',
                                 reply_markup=await keyboard.same_word(index, word_to_add, origin))
        else:
            await message.answer(text=f'<b>"{word_to_add}"</b> теперь в вашем избранном! ⭐️',
                                 parse_mode='html')
            await managing_favorites.add_to_favorites(message.from_user.id, en_word, ru_word)




@router_adding.callback_query(F.data.startswith('add'))
async def add_same_word(callback: CallbackQuery):
    data = callback.data.split('_')
    index = int(data[1])
    word_to_add = data[2]
    origin = data[3]
    tg_id = callback.from_user.id
    en_word, ru_word = await spelling.define_lang(word_to_add, origin, None)

    try:
        en_word_confirm, ru_word_confirm = await managing_favorites.managing_indexes(tg_id, index,
                                                                                     delete=False)
        if en_word.lower() == en_word_confirm.lower() and ru_word.lower() == ru_word_confirm.lower():
            await managing_favorites.managing_indexes(tg_id, index, delete=True)

    except TypeError:
        pass

    en_word = en_word.capitalize()
    ru_word = ru_word.capitalize()

    await managing_favorites.add_to_favorites(tg_id, en_word, ru_word)
    await callback.message.edit_text(text=f'<b>"{word_to_add}"</b> теперь в вашем избранном! ⭐️',
                         parse_mode='html')



@router_adding.callback_query(F.data == 'del')
async def deleting_same_word(callback: CallbackQuery):
    await callback.message.delete()



@router_adding.message(Command('mark'))
async def mark(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    args = command.args
    tg_id = message.from_user.id
    count = await back_viewing.view_favorites(tg_id, None, True)

    if count == 0:
        await message.answer(text='<b>У вас пока нету избранного! Добавьте хотя-бы один элемент</b> 🌟',
                             parse_mode='html')
        return

    if not args:
        args = str(count)

    try:
        number = int(args)
        if args[0] == '0' or number < 1:
            await message.answer(text='<b>Число должно быть положительным!</b> ❌', parse_mode='html')
            return

    except ValueError:
        await message.answer(text='<b>Сообщение должно содержать айди строки, '
                                  'которую вы хотите пометить!</b> ❌', parse_mode='html')
        return

    if number > count:
        await message.answer(text=f'<b>Айди <code>"{number}"</code> не существует!</b> ❌', parse_mode='html')
        return

    answer = await managing_favorites.marking(tg_id, number)
    await message.answer(text=answer, parse_mode='html')



@router_adding.callback_query(F.data.startswith('mark'))
async def mark_inline(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await callback.answer(text='Этот тест не доступен!', show_alert=True)
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message_id)
        return

    tg_id = callback.from_user.id
    mark_presence = callback.data.split('_')[1]
    step = data["step"]
    count = data["count"]
    answer = data["answer"].split(spelling.separate)
    main_accuracy = answer[0]
    suggested_word = answer[1]
    correct_word = answer[2]
    user_word = answer[3]
    en_word, ru_word = await spelling.define_lang(suggested_word, correct_word, None)

    index = await back_viewing.check_word(tg_id, en_word, ru_word, None)
    await managing_favorites.marking(tg_id, index)

    if mark_presence == '':
        mark_presence = f'{spelling.mark}  '
    else:
        mark_presence = ''

    await bot.edit_message_text(text=f'<i>{step} из {count}</i>\n\n'
                                     f'Твой ответ совпал на <b>{main_accuracy} %</b>!\n\n'
                                     f'{mark_presence}<b>{suggested_word}</b>  —  '
                                     f'<code>{correct_word}</code>\n\n'
                                     f'<i>Ваш ответ :</i>  <b>{user_word}</b>',
                                message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                                parse_mode='html', reply_markup=await keyboard.test(None, mark_presence))
