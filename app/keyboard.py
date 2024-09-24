from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.favorites.viewing.back_viewing import (view_favorites, text_of_lang,
                                                vis_able, vis_name, rand_option, len_of_page)
from app.additional.massive import switching
from aiogram.utils.keyboard import InlineKeyboardBuilder



async def translating(texts: any, example: any, translated_word: any):
    keyboard = InlineKeyboardBuilder()

    if example == None:
        keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data=f"back_ex_{texts}"))
        return keyboard.as_markup()

    keyboard.add(InlineKeyboardButton(text='🔄', callback_data=f"cycle_{translated_word}"))

    if example:
        keyboard.add(InlineKeyboardButton(text='Примеры использования 📓', callback_data=f"ex_{texts}"))

    return keyboard.adjust(1).as_markup()



async def favorites(page: int, tg_id: int, lang: int, vis: int, rand: int):
    words_count = await view_favorites(tg_id, page=None, words_count=True)
    all_pages = ((words_count - 1) + len_of_page) // len_of_page

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⬅️',
                              callback_data=
                              f"switch_{page - 1}_{switching[lang]}_{switching[vis]}_{switching[rand]}"),
        InlineKeyboardButton(text=f'{page} / {all_pages}',
                             callback_data=
                             f"pages_info_{page}_{all_pages}"),
        InlineKeyboardButton(text='➡️',
                             callback_data=
                             f"switch_{page + 1}_{switching[lang]}_{switching[vis]}_{switching[rand]}")],
        [InlineKeyboardButton(text=text_of_lang[lang],
                              callback_data=
                              f"switch_{page}_{switching[lang-1]}_{switching[vis]}_{switching[rand]}")],
        [InlineKeyboardButton(text=f'Видимость текста 😶‍🌫️ {vis_able[vis_name[vis]]}',
                              callback_data=
                              f"switch_{page}_{switching[lang]}_{switching[vis-1]}_{switching[rand]}")],
        [InlineKeyboardButton(text=rand_option[rand],
                              callback_data=
                              f"switch_{page}_{switching[lang]}_{switching[vis]}_{switching[rand-1]}")]
    ])
    return keyboard



async def same_word(index: int, word_to_add: str, origin: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data=f'add_{index}_{word_to_add}_{origin}'),
         InlineKeyboardButton(text='Нет', callback_data='del')]
    ])
    return keyboard



async def test(count: any, mark_presence: any):
    if count:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='🇷🇺', callback_data=f'test_{count}_0'),
                 InlineKeyboardButton(text='🇬🇧', callback_data=f'test_{count}_1')]
        ])
        return keyboard

    else:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text='Дальше ➡️', callback_data=f'test'))

        if mark_presence == '':
            keyboard.add(InlineKeyboardButton(text='Пометить ✔️', callback_data=f'mark_{mark_presence}'))
        else:
            keyboard.add(InlineKeyboardButton(text='Убрать метку ✖️', callback_data=f'mark_{mark_presence}'))
        return keyboard.as_markup()



