from sqlalchemy import select
from app.database import async_session
from app.database import User
import app.additional.spelling as spelling



async def add_to_favorites(tg_id: int, en_word: str, ru_word: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        en_column = user.en_column
        ru_column = user.ru_column

        en_column += en_word + spelling.separate
        ru_column += ru_word + spelling.separate

        user.en_column = en_column
        user.ru_column = ru_column
        user.words_count += 1
        await session.commit()



async def add_words_list(tg_id: int, words_to_add: any, is_add: bool):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if is_add:
            user.current_words = words_to_add
            await session.commit()
        else:
            return user.current_words



async def managing_indexes(tg_id: int, index: int, delete: bool):
    async with (async_session() as session):
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if index == -1:
            index = user.words_count

        en_column = user.en_column.split(spelling.separate)
        ru_column = user.ru_column.split(spelling.separate)

        if not delete:
            en_word = en_column[index - 1]
            ru_word = ru_column[index - 1]
            return en_word, ru_word

        del en_column[index - 1]
        del ru_column[index - 1]
        en_column = spelling.separate.join(en_column)
        ru_column = spelling.separate.join(ru_column)

        user.en_column = en_column
        user.ru_column = ru_column
        user.words_count -= 1
        await session.commit()
        return index



async def marking(tg_id: int, index: int):
    en_word, ru_word = await managing_indexes(tg_id, index, False)
    order = (await spelling.define_mark(en_word, ru_word, index))[2]

    if order == index:
        en_word = f'{spelling.mark}{en_word}'
        ru_word = f'{spelling.mark}{ru_word}'
        answer = (f'<i>Запись с айди <code>"{index}"</code> помечена в вашем избранном</i> 💫\n\n'
                  f'{spelling.mark}<b>{index}</b>.  <b>{en_word[2:]}  —</b>  <code>{ru_word[2:]}</code>')

    else:
        en_word = en_word[2:]
        ru_word = ru_word[2:]
        answer = (f'<i>Отметка со строки <code>"{index}"</code> убрана</i> 💫\n\n'
                  f'<b>{index}.</b>  {en_word}  <b>—</b>  <code>{ru_word}</code>')

    await managing_indexes(tg_id, index, True)
    await add_to_favorites(tg_id, en_word, ru_word)
    return answer
