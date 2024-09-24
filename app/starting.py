from app.database import async_session
from app.database import User
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from aiogram import Router
router_start = Router()

@router_start.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await registration(message)
    await message.answer('<b>Привет, это переводчик</b>', parse_mode='html')


async def registration(message: Message):
    async with async_session() as session:
        tg_id = message.from_user.id
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:

            if message.from_user.username == None:
                tg_user = 'None'
            else:
                tg_user = message.from_user.username

            session.add(User(tg_id=tg_id, tg_user=tg_user, en_column='', ru_column='',
                             current_words='', words_count=0))
            await session.commit()
            