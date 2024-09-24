from aiogram.types import Message
from aiogram import Router, F, Bot
from config import token
import app.additional.spelling as spelling
import app.translating.back_translating as back_translating
import app.translating.front_translating as front_translating
from aiogram.types import CallbackQuery
import app.keyboard as keyboard
router_translating = Router()
bot = Bot(token=token)



@router_translating.message(F.text)
async def translating(message: Message):
    text_spelling = await spelling.check_spelling(message.text)
    if not text_spelling:
        await message.answer(text='<b>Некорректный ввод!</b> ❌', parse_mode='html')
        return

    text = text_spelling[0]
    from_lang = text_spelling[1]
    to_lang = text_spelling[2]
    bot_message = await message.answer(text='⏳ <b>Ожидайте сообщения ...</b>', parse_mode='html')
    chat_id = message.chat.id
    if await front_translating.main_translating(bot_message.message_id, chat_id, text, from_lang,
                                                to_lang, message.from_user.id, current_words=True):
        await bot.edit_message_text(text='<b>Произошла неизвестная ошибка!</b> Попробуйте снова',
                                    chat_id=chat_id, message_id=bot_message.message_id, parse_mode='html')


@router_translating.callback_query(F.data[:2] == 'ex')
async def open_examples_call(callback: CallbackQuery):
    texts = callback.data[3:]
    origin_text = texts.split('_')[0]
    translate_text = texts.split('_')[1]
    text = (await spelling.define_lang(origin_text.lower(), translate_text.lower(), None))[0]
    examples = await back_translating.get_translate(text, "en", "ru", 'ex', False)

    if examples:
        await callback.message.edit_text(text='💫 <b>Подождите некоторое время ...</b>', parse_mode='html')
        answer = '<b>ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ 🗒</b>\n\n'

        for el in range(len(examples)):
            under_example = await back_translating.get_translate(examples[el], "en", "ru", 't', None)
            answer += f"<code>{el+1}.</code> {examples[el]}\n<i>{under_example}</i>\n\n"

        await callback.message.edit_text(answer, parse_mode='html', reply_markup=
                                         await keyboard.translating(origin_text, example=None,
                                                                    translated_word=None))
    else:
        await callback.answer(
            text=f'Похоже что примеров с "{origin_text}" не существует 🙄', show_alert=True)



@router_translating.callback_query(F.data[:7] == 'back_ex')
async def back_examples_call(callback: CallbackQuery):
    text = callback.data.split('_')[2]
    await translating_again(callback, text, current_words=False)



@router_translating.callback_query(F.data.startswith('cycle'))
async def cycle(callback: CallbackQuery):
    translated_word = callback.data.split('_')[1]
    await translating_again(callback, translated_word, current_words=True)



async def translating_again(callback: CallbackQuery, text: str, current_words: bool):
    await callback.message.edit_text(text='💫 <b>Подождите некоторое время ...</b>', parse_mode='html')
    message_id = callback.message.message_id
    chat_id = callback.message.chat.id
    text_spelling = await spelling.check_spelling(text)
    text = text_spelling[0]
    from_lang = text_spelling[1]
    to_lang = text_spelling[2]
    if await front_translating.main_translating(message_id, chat_id, text, from_lang, to_lang,
                                                callback.from_user.id, current_words):
        await bot.edit_message_text(text='<b>Произошла неизвестная ошибка!</b> Попробуйте снова',
                                    chat_id=chat_id, message_id=message_id, parse_mode='html')
