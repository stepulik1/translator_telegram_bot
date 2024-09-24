from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
import app.keyboard as keyboard
from aiogram.fsm.context import FSMContext
import app.favorites.viewing.back_viewing as back_viewing
import app.favorites.managing_favorites as managing_favorites
from aiogram.exceptions import TelegramBadRequest
import app.additional.spelling as spelling
router_viewing = Router()



@router_viewing.message(Command('words'))
async def view_words(message: Message, state: FSMContext):
    await state.clear()
    column = await back_viewing.view_favorites(message.from_user.id, page=1, words_count=False)
    if not column:
        await message.answer(text='<b>У вас пока нету избранного! Добавьте хотя-бы один элемент</b> 🌟',
                             parse_mode='html')
        return

    answer = '<i>ВАШИ ИЗБРАННЫЕ</i> 🌟\n\n'
    favorites = await back_viewing.get_favorites(column, html='code', rand=0, place=0)
    answer += favorites
    await message.answer(answer, parse_mode='html',
                         reply_markup=await keyboard.favorites(
                                 page=1, tg_id=message.from_user.id, lang=0, vis=0, rand=0))



@router_viewing.callback_query(F.data.startswith('switch'))
async def switch_page(callback: CallbackQuery):
    words_count = await back_viewing.view_favorites(callback.from_user.id, page=None, words_count=True)
    if words_count == 0:
        await callback.message.edit_text(text='<b>У вас пока нету избранного! '
                                              'Добавьте хотя-бы один элемент</b> 🌟',
                                         parse_mode='html')
        return

    data = callback.data.split('_')
    page = int(data[1])
    lang = int(data[2])
    vis = int(data[3])
    rand = int(data[4])
    all_pages = ((words_count - 1) + back_viewing.len_of_page) // back_viewing.len_of_page

    if page > all_pages:
        page = 1
    elif page < 1:
        page = all_pages

    column = await back_viewing.view_favorites(callback.from_user.id, page=page, words_count=False)
    answer = '<i>ВАШИ ИЗБРАННЫЕ</i> 🌟\n\n'
    favorites = await back_viewing.get_favorites(column, back_viewing.vis_name[vis], rand, place=lang)
    answer += favorites

    try:
        await callback.message.edit_text(answer, parse_mode='html',
                                         reply_markup=await keyboard.favorites(
                                                 page=page, tg_id=callback.from_user.id,
                                                 lang=lang, vis=vis, rand=rand))
    except TelegramBadRequest:
        await callback.answer()



@router_viewing.callback_query(F.data.startswith('pages_info'))
async def switch_page(callback: CallbackQuery):
    data = callback.data.split('_')
    page = data[2]
    all_pages = data[3]
    await callback.answer(f'{page} страница из {all_pages} ✨')



@router_viewing.message(Command('s'))
async def search_words(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    args = command.args

    if not args:
        await message.answer(text='<b>Сообщение должно содержать айди строки или текст!</b> ❌',
                             parse_mode='html')
        return

    tg_id = message.from_user.id

    try:
        id_to_search = int(args)
        if args[0] == '0' or id_to_search < 1:
            await message.answer(text='<b>Число должно быть больше нуля!</b> ❌', parse_mode='html')
            return

        if id_to_search > await back_viewing.view_favorites(tg_id, page=None, words_count=True):
            await message.answer(text='<b>Строки с таким айди не существует!</b> ❌', parse_mode='html')
            return

        en_word, ru_word = await managing_favorites.managing_indexes(tg_id, id_to_search, delete=False)
        await message.reply(text=f'<i>Строка с айди <code>"{id_to_search}"</code></i> 🌟\n\n'
                                 f'<b>{id_to_search}.</b>  {en_word}  <b>—</b>  '
                                 f'<code>{ru_word}</code>', parse_mode='html')

    except ValueError:
        word_to_search = args
        en_word, ru_word = await spelling.define_lang(word_to_search, None, None)
        ids_to_search = await back_viewing.check_word(tg_id, en_word=en_word, ru_word=ru_word, accuracy=70)
        answer = ''

        for index in ids_to_search:
            en_word, ru_word = await managing_favorites.managing_indexes(tg_id, index, delete=False)
            marking_data = await spelling.define_mark(en_word, ru_word, '')
            en_word, ru_word, order = marking_data[0], marking_data[1], marking_data[2]

            if order == spelling.mark:
                en_word = f'<b>{en_word}</b>'

            answer += f'{order}<b>{index}</b>.  {en_word}  —  <code>{ru_word}</code>\n\n'

        if answer:
            answer = (f'<i>Нашлось несколько записей, схожих со словом <code>"{word_to_search}"</code></i> 🌟'
                      f'\n\n{answer[:-2]}')
        else:
            answer = f'<i>Похоже, что ничего не нашлось со словом <code>"{word_to_search}"</code></i> 🙁'

        await message.answer(text=answer, parse_mode='html')


