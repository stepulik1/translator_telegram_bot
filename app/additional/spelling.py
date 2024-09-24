import asyncio
import re
from string import digits
from string import ascii_lowercase
from difflib import SequenceMatcher
import app.additional.massive as massive
ru_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

other_symbols = """ ,!?.♪μΠΩ¶₹¥₱←↑↓→≠∞≈‰℅№±·—–_‡†★”„“«»‹›‘’¡¿‽~`
                |•√π÷×§∆£€$¢^°={}\%©®™✓[]<>@#₽_&-+()/"*':;ω⭐️"""

restricted_symbols = ['<b>', '</b>', '<i>', '</i>', '<u>', '</u>', '<code>', '</code>']

ending_symbols = '!?.\n|;'

mark = '⭐️'

separate = 'º'

type_of_speech = {'noun': 'cуществительное', 'verb': 'глагол', 'conjunction': 'конъюнкция',
                  'pronoun': 'местоимение', 'adjective': 'прилагательное', 'preposition': 'предлог',
                  '': 'числительное', 'adverb': 'наречие'}

async def find_emoji(text):
    loop = asyncio.get_event_loop()
    emoji_pattern = re.compile(pattern="["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F700-\U0001F77F"
                               u"\U0001F780-\U0001F7FF"
                               u"\U0001F800-\U0001F8FF"
                               u"\U0001F900-\U0001F9FF"
                               u"\U0001FA00-\U0001FA6F"
                               u"\U0001FA70-\U0001FAFF"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)

    return await loop.run_in_executor(None, emoji_pattern.search, text)



async def check_spelling(text: str):
    text = text.lower()

    for restrict in restricted_symbols:
        if restrict in text:
            return

    if await find_emoji(text):
        for letter in text:
            if letter in other_symbols:
                break
        else:
            return

    if all(letter in other_symbols for letter in text):
        return

    result = await define_lang(text, None, True)
    if result:
        text_info = ["en", "ru"]
    elif result is False:
        text_info = ["ru", "en"]
    else:
        return

    text = [await massive.check_if_massive(text)]
    return text + text_info



async def define_lang(first_word: str, second_word: any, direction: any):
    if direction is None:
        for letter in first_word:
            if letter.lower() in ascii_lowercase:
                return first_word, second_word

            if letter.lower() in ru_alphabet:
                return second_word, first_word

    elif direction is True:
        if all((letter in ascii_lowercase or letter in (other_symbols + digits)) for letter in first_word.lower()):
            return True

        if all((letter in ru_alphabet or letter in (other_symbols + digits)) for letter in first_word.lower()):
            return False

    return None



async def check_accuracy(user_word: str, correct_word: str):
    matcher = SequenceMatcher(None, user_word, correct_word)
    similarity_ratio = matcher.ratio() * 100
    return round(similarity_ratio)



async def define_mark(first_word: str, second_word: any, numbering: any):
    is_mark_up = numbering

    if first_word[:2] == mark:
        first_word = first_word[2:]
        is_mark_up = mark

        if second_word:
            second_word = second_word[2:]

    return [first_word, second_word, is_mark_up]
