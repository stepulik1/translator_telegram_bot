from random import randint
import app.additional.spelling as spelling
from aiogram.types import Message

switching = [0, 1]

commands = ['/end', '/test', '/words', '/del', ]


async def get_random_values(length: int):
    random_values = []
    while len(random_values) != length:
        value = randint(a=0, b=length - 1)
        if value not in random_values:
            random_values.append(value)

    return random_values


def set_lists(items):
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result



async def check_if_massive(text: str):
    all_text_massives = []

    for symbol in spelling.ending_symbols:
        if symbol in text:
            text_massive = []
            start = end = 0

            for letter in text:
                if letter == symbol:
                    text_massive.append(text[start:end + 1])
                    start = end + 1
                end += 1

            if start != end:
                text_massive.append(text[start:end])

            all_text_massives.append(text_massive)

    if len(all_text_massives) == 1 and len(all_text_massives[0]) == 1:
        return all_text_massives[0][0].capitalize()

    if len(all_text_massives) > 0:
        text = []
        min_text_index = 0
        min_text = 1000
        while True:
            try:
                for massive in range(len(all_text_massives)):
                    if len(all_text_massives[massive][0]) < min_text:
                        min_text = len(all_text_massives[massive][0])
                        min_text_index = massive
            except IndexError:
                break

            new_text = all_text_massives[min_text_index][0]
            del all_text_massives[min_text_index][0]
            excess_symbol = True

            for letter in new_text:
                if letter not in spelling.other_symbols:
                    excess_symbol = False
                    break

            if excess_symbol:
                text[-1] += new_text
            else:
                text.append(new_text.strip().capitalize())

            for massive in range(len(all_text_massives)):
                if massive == min_text_index:
                    continue
                text_massive = spelling.separate. join(all_text_massives[massive])
                text_massive = text_massive[min_text:]
                all_text_massives[massive] = text_massive.split(spelling.separate)

            min_text = 1000
        return text
    return text.capitalize()



async def check_valid_number(args: str, words_count: int, message: Message):
    if not args:
        number = words_count
        return number

    try:
        if '-' in args:
            raise ValueError

        number = int(args)
        if number < 1 or args[0] == '0':
            await message.answer(text='<b>Число должно быть больше нуля!</b> ❌', parse_mode='html')
            return

    except ValueError:
        if '-' not in args:
            await message.answer(text='<b>Требуется одно число!</b> ❌', parse_mode='html')
            return

        numbers = args.split('-')

        if len(numbers) != 2:
            await message.answer(text='<b>Введите промежуток, который вы хотите удалить!</b> ❌',
                                 parse_mode='html')

        first_number, second_number = numbers[0], numbers[1]

        if not first_number:
            first_number = '1'

        if not second_number:
            second_number = str(words_count)

        first_number = await check_valid_number(first_number, words_count, message)
        if not first_number:
            return

        second_number = await check_valid_number(second_number, words_count, message)
        if not second_number:
            return

        if first_number > second_number:
            await message.answer(text='<b>Ваше первое число больше второго!</b> ❌', parse_mode='html')
            return

        numbers = [first_number, second_number]
        return list(set(numbers))

    if number > words_count:
        await message.answer(text='<b>Строки с таким айди не существует</b> 🙄',
                             parse_mode='html')
        return

    return number

