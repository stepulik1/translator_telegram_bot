import aiohttp
from aiohttp.client_exceptions import ClientConnectionError
from asyncio import TimeoutError
import app.additional.spelling as spelling
from aiogram.exceptions import TelegramNetworkError
import app.additional.massive as massive


async def get_translate(text, from_lang: str, to_lang: str, direct: str, text_is_list: any):
    able_another_data_at = False
    if text[-1] == spelling.separate:
        text = text[:-1]
        able_another_data_at = True

    if text_is_list:
        other_words = []
        max_length = 'first'

        for item in text:
            data = await get_translate(item, from_lang, to_lang, "at", False)
            position = 0
            length_data = len(data)

            if max_length == 'first':
                max_length = length_data

            while length_data < max_length:
                del other_words[max_length - 1]
                max_length -= 1

            for other_word in range(max_length):
                try:
                    if other_words[position][-1] not in spelling.other_symbols:
                        other_words[position] = other_words[position] + ' '

                    other_words[position] += data[other_word]
                except IndexError:
                    other_words.append(data[other_word])
                position += 1
        return ['АЛЬТЕРНАТИВЫ', other_words]

    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": from_lang,
        "tl": to_lang,
        "dt": direct,
        "q": text
    }
    async with aiohttp.ClientSession() as session:
        try:
            response = await session.get(url, params=params, timeout=3)

            if response.status != 200:
                return None

            result = await response.json()
            if direct == 'ex':
                examples = []
                try:
                    data = result[13][0]
                except IndexError:
                    return None
                for el in data:
                    examples.append(el[0])
                return examples

            if direct == "md":
                try:
                    definition = result[12][0][1][0][0]
                    return definition
                except IndexError:
                    return None

            if direct == 't':
                return result[0][0][0]

            if direct == 'at':
                data_at = result[5][0][2]
                other_words = []

                for el in data_at:
                    other_word = el[0].capitalize()
                    other_words.append(other_word)

                if able_another_data_at:
                    return other_words

                another_data_at = []
                if len(text) < 30:
                    if text == text.lower():
                        text = text.capitalize()
                        another_data_at = await get_translate(text + spelling.separate,
                                                              from_lang, to_lang, 'at', text_is_list)
                    else:
                        another_data_at = await get_translate(text.lower() + spelling.separate,
                                                              from_lang, to_lang, 'at', text_is_list)

                other_words = massive.set_lists(other_words + another_data_at)
                data_bd = await get_translate(text, from_lang, to_lang, 'bd', text_is_list)

                if not data_bd:
                    head = 'АЛЬТЕРНАТИВЫ'
                    if text_is_list is None:
                        return [head, other_words]
                    else:
                        return other_words

                else:
                    head = 'СЛОВАРЬ'
                    type_of_word = data_bd[1]
                    alternatives_test = data_bd[0]
                    alternatives = []

                    for el in alternatives_test:

                        if el[0].capitalize() not in other_words:
                            if text_is_list is None:
                                alternatives.append(el)
                            else:
                                alternatives.append(el[0])

                    if text_is_list is None:
                        return [head, other_words, alternatives, type_of_word]
                    else:
                        return other_words + alternatives

            if direct == 'bd':
                if result[1] == None:
                    return None
                type_of_word = result[1][0][0]
                alternatives = []
                stop = 0
                for el in result[1][0][2]:
                    stop += 1
                    alternatives.append([el[0], el[1][0]])
                    if stop == 15:
                        break
                return [alternatives, type_of_word]

        except ClientConnectionError:
            return await get_translate(text, from_lang, to_lang, direct, text_is_list)

        except TelegramNetworkError:
            return await get_translate(text, from_lang, to_lang, direct, text_is_list)

        except TimeoutError:
            return await get_translate(text, from_lang, to_lang, direct, text_is_list)
