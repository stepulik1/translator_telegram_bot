from aiogram import Bot
from config import token
from aiogram.exceptions import TelegramBadRequest
import app.translating.back_translating as back_translating
import app.favorites.managing_favorites as managing_favorites
import app.additional.spelling as spelling
import app.keyboard as keyboard

bot = Bot(token=token)

emoji_of_words = ['📕', '📗', '📘', '📙']


async def main_translating(message_id: int, chat_id: int, text: str, from_lang: str,
                           to_lang: str, tg_id: int, current_words: bool):
    text_is_list = None
    text_to_translate = text

    if isinstance(text, list):
        text_is_list = True
        text = ''.join(text)

    translated_data = await back_translating.get_translate(text_to_translate, from_lang, to_lang, 'at', text_is_list)
    if not translated_data:
        await bot.edit_message_text(text='<b>Произошла неизвестная ошибка!</b> Попробуйте снова',
                                    chat_id=chat_id, message_id=message_id, parse_mode='html')
        return

    head = translated_data[0]
    translated_word = translated_data[1][0]
    words_to_add = text.capitalize() + spelling.separate + translated_word.capitalize() + spelling.separate
    translated_words = translated_data[1][1:]

    if translated_words:
        chapter = '\n\n<b>1.</b>  '
        top = 2
    else:
        chapter = ''
        top = 1

    if len(text) >= 30:
        large_text = '\n'
    else:
        large_text = ''

    if head == 'СЛОВАРЬ':
        try:
            alternatives = translated_data[2]
        except IndexError:
            alternatives = []

        alternatives_length = len(alternatives)
        speech_of_word = translated_data[3]

        if from_lang == "en":
            definition = await back_translating.get_translate(translated_word, to_lang, from_lang, 'md', None)
        else:
            definition = await back_translating.get_translate(text, from_lang, to_lang, 'md', None)

        if definition:
            definition = f"<b>ОПРЕДЕЛЕНИЕ</b> 📄: <i>{definition}</i>\n\n"
        else:
            definition = ''

        answer = (f"<b>{text}  ›››  {large_text}<code>{translated_word}</code></b>"
                  f"\n\n{definition}<b>{head}</b> 📚:"
                  f"\n<b><u>{text.upper()}</u></b> {spelling.type_of_speech[speech_of_word]} 🌟{chapter}")
        under_translate = f""
        emoji_type = 0

        for word in translated_words:
            try:
                word = word.capitalize()
            except AttributeError:
                return True

            answer += f"<code>{word}</code>,  "
            under_translate += (
                f"<i>{await back_translating.get_translate(word, to_lang, from_lang,'t', None)}</i>,  ")
            words_to_add += word.capitalize() + spelling.separate

        for el in range(alternatives_length):
            if el // 5 == 3:
                emoji_type = el
                break

            if el % 5 == 0:
                if translated_words:
                    answer = answer[:-3] + f"{emoji_of_words[el // 5]}\n" + under_translate[:-3]
                under_translate = f""
                answer += f"\n\n<b>{(el // 5) + top}.</b>  "

            word_up = alternatives[el][0][0].upper() + alternatives[el][0][1:].lower()
            word_under = alternatives[el][1][0].upper() + alternatives[el][1][1:].lower()
            answer += f"<code>{word_up}</code>,  "
            under_translate += f"<i>{word_under}</i>,  "
            words_to_add += word_up.capitalize() + spelling.separate

            if el == alternatives_length - 1:
                emoji_type = (alternatives_length - 1) + 5

        if translated_words or alternatives:
            answer = answer[:-3] + f"{emoji_of_words[emoji_type // 5]}\n" + under_translate[:-3]

        texts = text + '_' + translated_word
        example = True

    else:

        answer = (f"<b>{text}  ›››  {large_text}<code>{translated_word}</code></b>"
                  f"\n\n<b>{head}</b> 📚:")

        for el in range(len(translated_words)):
            if el > 3:
                break
            word = translated_words[el]
            answer += (f"\n\n<b>{el + 1}.</b>  <code>{word}</code> {emoji_of_words[el]}\n"
                       f"<i>{await back_translating.get_translate(word, to_lang, from_lang, 't', None)}</i>")
            words_to_add += word.capitalize() + spelling.separate

        texts = None
        example = False

    if current_words:
        await managing_favorites.add_words_list(tg_id, words_to_add[:-1], is_add=True)

    if '<' in answer or '>' in answer:

        if '<' in answer:
            answer = answer.replace('<', '&lt;')
        if '>' in answer:
            answer = answer.replace('>', '&gt;')

        for symbol in ['i', 'b', 'u', 'code']:
            answer = answer.replace(f'&lt;{symbol}&gt;', f'<{symbol}>')
            answer = answer.replace(f'&lt;/{symbol}&gt;', f'</{symbol}>')

    try:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=answer, parse_mode='html',
                                    reply_markup=await keyboard.translating(texts, example=example,
                                                                            translated_word=translated_word))
    except TelegramBadRequest:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=answer, parse_mode='html')
