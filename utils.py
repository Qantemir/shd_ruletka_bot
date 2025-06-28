import random
import asyncio
import os
from aiogram.types import Message

async def spin_roulette(message: Message, prizes: list, review_link: str):
    shown_msg = await message.answer("🎯 Запускаем рулетку...")

    animation_frames = [
        "🎯 Запускаем рулетку...",
        "🎲 Крутим барабан...",
        "🎰 Выбираем лучший приз...",
        "🎁 Почти на месте...",
        "✨ Всё готово!"
    ]

    for frame in animation_frames:
        try:
            await shown_msg.edit_text(frame)
        except:
            pass
        await asyncio.sleep(0.7)

    final_prize = random.choice(prizes)
    # Продающий текст
    prize_text = (
        f"<b>Внимание!</b><i>Участие в акции — только один раз на стол.</i>\n\n"
        f"🎁 Ваш приз: <b>{final_prize['name']}</b>\n\n"
        f"<b>Мало призов?</b>\n"
        f"💬 Мы дарим <b>дополнительную скидку 5%</b> за ваш отзыв "
        f"<a href='{review_link}'>Оставьте короткий отзыв в 2GIS</a> — это займёт всего минуту, а нам будет очень приятно!\n\n"
        f"🧑‍🍳 Для получения приза пожалуйста обратитесь к официанту.\n\n"
    )

    await message.answer(prize_text, parse_mode="HTML")

    return final_prize
