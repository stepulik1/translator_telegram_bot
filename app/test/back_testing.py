from aiogram.fsm.context import FSMContext
from aiogram import Bot
from config import token
import app.keyboard as keyboard
from app.database import async_session
from app.database import User
from sqlalchemy import select
import app.additional.massive as massive
import app.additional.spelling as spelling
import app.test.testing_queries as testing_queries
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
import random


bot = Bot(token=token)



async def in_process_test(message: Message, state: FSMContext):
    data = await state.get_data()
    step = data["step"]
    count = data["count"]
    message_id = data["message_id"]

    if step == 0:
        head = '<i>Ваша проверка грамматики началась!</i>\n\n'

    elif step == count:
        await state.update_data(available_test=False)
        return True

    else:
        head = ''

    test_words = data["words"]
    suggested_word = test_words[step][0]
    correct_words = test_words[step][1]
    await state.update_data(correct_words=correct_words, suggested_word=suggested_word)

    try:
        await bot.edit_message_text(text=f'{head}<i>{step + 1} из {count}</i>\n\n'
                                     f'Как переводится <b>{suggested_word}</b>?',
                                    chat_id=message.chat.id, message_id=message_id, parse_mode='html')
    except TelegramBadRequest:
        return True




async def in_answer_test(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(delete_message=data["delete_message"] + [message.message_id])
    message_id = data["message_id"]
    user_word = message.text
    suggested_word = data["suggested_word"]
    correct_words = data["correct_words"]
    restriction = data["restriction"]
    final_accuracy = data["final_accuracy"]
    step = data["step"]
    count = data["count"]

    if len(correct_words) == 1:
        correct_word = correct_words[0]
        marking_data = await spelling.define_mark(correct_word, None, '')
        correct_word, mark_presence = marking_data[0], marking_data[2]
        main_accuracy = await spelling.check_accuracy(user_word.strip().lower(), correct_word.strip().lower())

    else:
        accuracy_values = []

        if suggested_word in restriction.keys():
            restricted_words = list(restriction[suggested_word])[0]
        else:
            restricted_words = []

        for right_word in correct_words:

            if right_word in restricted_words:
                accuracy = -1

            else:
                right_word = (await spelling.define_mark(right_word, None, None))[0]
                accuracy = await spelling.check_accuracy(user_word.strip().lower(), right_word.strip().lower())

            accuracy_values.append(accuracy)

        main_accuracy = max(accuracy_values)
        index_likely_word = accuracy_values.index(main_accuracy)
        correct_word = correct_words[index_likely_word]

        try:
            restriction[suggested_word].append(correct_word)
        except KeyError:
            restriction[suggested_word] = [correct_word]

        marking_data = await spelling.define_mark(correct_word, None, '')
        correct_word, mark_presence = marking_data[0], marking_data[2]

    final_accuracy += main_accuracy
    step += 1

    answer = (f'{main_accuracy}{spelling.separate}{suggested_word}'
              f'{spelling.separate}{correct_word}{spelling.separate}{user_word}')

    await state.update_data(step=step, restriction=restriction,
                            final_accuracy=final_accuracy, answer=answer)

    if mark_presence == spelling.mark:
        mark_presence = mark_presence + '  '

    try:
        await bot.edit_message_text(text=f'<i>{step} из {count}</i>\n\n'
                                         f'Твой ответ совпал на <b>{main_accuracy} %</b>!\n\n'
                                         f'{mark_presence}<b>{suggested_word}</b>  —  '
                                         f'<code>{correct_word}</code>\n\n'
                                         f'<i>Ваш ответ :</i>  <b>{user_word}</b>',
                                    message_id=message_id, chat_id=message.chat.id, parse_mode='html',
                                    reply_markup=await keyboard.test(None, mark_presence))
    except TelegramBadRequest:
        return True



async def get_test_words(tg_id: int, lang: int, count: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        length = user.words_count

        en_column = user.en_column[:-1]. split(spelling.separate)
        ru_column = user.ru_column[:-1]. split(spelling.separate)
        total_column = [ru_column, en_column]
        column = []
        words_with_reps = {}

        for value in range(length):
            first_word = total_column[lang][value]
            second_word = total_column[massive.switching[lang - 1]][value]
            first_word = (await spelling.define_mark(first_word, None, None))[0]

            try:
                words_with_reps[first_word].append(second_word)
                word_with_reps = words_with_reps[first_word]
                random.shuffle(word_with_reps)

                for el in range(len(column)):
                    if first_word == column[el][0]:
                        column[el][1] = word_with_reps

                column.append([first_word, word_with_reps])

            except KeyError:
                words_with_reps[first_word] = [second_word]
                column.append([first_word, [second_word]])

        random_values = await massive.get_random_values(count)
        column = column[length - count:]
        random_column = []

        for value in random_values:
            random_column.append([column[value][0], column[value][1]])

        return random_column
