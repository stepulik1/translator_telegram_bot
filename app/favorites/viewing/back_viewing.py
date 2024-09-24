import app.additional.massive as massive
from app.database import async_session
from app.database import User
from sqlalchemy import select
import app.additional.spelling as spelling

text_of_lang = ['🇷🇺 » 🇬🇧', '🇬🇧 » 🇷🇺']


vis_able = {'code': '☑️', 'tg-spoiler': '✖️'}


vis_name = ['code', 'tg-spoiler']


len_of_page = 10


rand_option = ['Перемешать 🎲', 'Восстановить 🍀']


async def get_favorites(column: list, html: str, rand: int, place: int):
    answer = ''
    length = len(column)
    if rand == 0:
        for el in range(length):
            marking_data = await spelling.define_mark(column[el][place],
                                                      column[el][massive.switching[place - 1]], '')
            first_word, second_word, order = marking_data[0], marking_data[1], marking_data[2]

            if order == spelling.mark:
                first_word = f'<b>{first_word}</b>'

            answer += f'{order}<b>{column[el][2]}</b>.  {first_word}  <b>—</b>  <{html}>{second_word}</{html}>\n\n'
    else:
        random_values = await massive.get_random_values(length)
        for el in random_values:
            marking_data = await spelling.define_mark(column[el][place], column[el][massive.switching[place - 1]], '·')
            first_word, second_word, mark_presence = marking_data[0], marking_data[1], marking_data[2]

            if mark_presence == spelling.mark:
                first_word = f'<b>{first_word}</b>'

            answer += f'<b>{mark_presence}</b>  {first_word}  <b>—</b>  <{html}>{second_word}</{html}>\n\n'

    return answer



async def view_favorites(tg_id: int, page: any, words_count: bool):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user.words_count == 0:
            return 0

        if words_count:
            return user.words_count

        en_column = user.en_column[:-1]
        ru_column = user.ru_column[:-1]

        start = (page * len_of_page) - len_of_page
        end = page * len_of_page
        order = (page * len_of_page) - len_of_page + 1

        en_column = en_column.split(spelling.separate)[start:end]
        ru_column = ru_column.split(spelling.separate)[start:end]
        column = []

        for el in range(len(en_column)):
            column.append([en_column[el], ru_column[el], order + el])

        return column



async def check_word(tg_id: int, en_word: any, ru_word: any, accuracy: any):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        en_column = user.en_column[:-1]. lower(). split(spelling.separate)
        ru_column = user.ru_column[:-1]. lower(). split(spelling.separate)

        try:
            marking_data = await spelling.define_mark(en_word.lower(), ru_word.lower(), None)
            en_word = marking_data[0]
            ru_word = marking_data[1]

            for el in range(user.words_count):
                marking_data = await spelling.define_mark(en_column[el], ru_column[el], None)
                en_word_confirm, ru_word_confirm = marking_data[0], marking_data[1]

                if en_word == en_word_confirm and ru_word == ru_word_confirm:
                    return el + 1
            return

        except AttributeError:
            suitable_words = []
            if not en_word:
                main_word = (await spelling.define_mark(ru_word.lower(), None, None))[0]
                main_column = ru_column
            else:
                main_word = (await spelling.define_mark(en_word.lower(), None, None))[0]
                main_column = en_column

            for el in range(user.words_count):
                if await spelling.check_accuracy(main_word, main_column[el]) >= accuracy:
                    suitable_words.append(el + 1)

            return suitable_words
