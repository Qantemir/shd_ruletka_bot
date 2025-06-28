from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json
from utils import spin_roulette
from database import user_already_played, save_user_spin, clean_old_spins
from logger import log_user_action, log_error

def get_unique_prizes(prizes):
    """Получить уникальные призы без повторений"""
    seen = set()
    unique_prizes = []
    for prize in prizes:
        if prize['name'] not in seen:
            seen.add(prize['name'])
            unique_prizes.append(prize)
    return unique_prizes

def create_welcome_message(prizes):
    """Создать приветственное сообщение со списком призов"""
    unique_prizes = get_unique_prizes(prizes)
    
    message = "🎉 Добро пожаловать в розыгрыш призов!\n\n"
    message += "🎁 Возможные призы:\n"
    
    for i, prize in enumerate(unique_prizes, 1):
        message += f"{i}. {prize['name']}\n"
    
    message += "\n🎯 Нажмите кнопку 'Крутить' чтобы попытать удачу!"
    
    return message

def register_handlers(dp):
    router = Router()

    @router.message(CommandStart())
    async def start_cmd(message: types.Message):
        try:
            if message.from_user is None:
                await message.answer("😔 Не удалось определить пользователя.")
                return

            user_id = message.from_user.id
            username = message.from_user.username or "Unknown"
            
            log_user_action(user_id, "start_command", f"Username: {username}")
            
            await clean_old_spins()
            
            # Загружаем конфигурацию
            with open("config.json", encoding="utf-8") as f:
                config = json.load(f)
            
            # Создаем приветственное сообщение
            welcome_text = create_welcome_message(config["prizes"])
            
            # Текст правил
            rules_text = (
                "<b>Внимание!</b>\n"
                "<i>Участие в акции — только один раз на стол.</i>\n\n"
            )
            
            # Создаем клавиатуру с кнопкой "Крутить"
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text="🎯 Крутить", callback_data="spin_roulette"))
            
            await message.answer(welcome_text, reply_markup=builder.as_markup())
            await message.answer(rules_text, parse_mode="HTML")
            
        except Exception as e:
            log_error(e, f"start_command for user {message.from_user.id if message.from_user else 'Unknown'}")
            await message.answer("😔 Произошла ошибка. Попробуйте позже.")

    @router.callback_query(F.data == "spin_roulette")
    async def spin_roulette_callback(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            username = callback.from_user.username or "Unknown"
            
            log_user_action(user_id, "spin_roulette_clicked", f"Username: {username}")
            
            # Проверяем, не участвовал ли пользователь уже сегодня
            if await user_already_played(user_id):
                await callback.answer("😅 Вы уже участвовали сегодня! Приходите завтра 🎁", show_alert=True)
                log_user_action(user_id, "already_played_today")
                return
            
            # Загружаем конфигурацию
            with open("config.json", encoding="utf-8") as f:
                config = json.load(f)
            
            # Проверяем, что callback.message доступно
            if callback.message is None:
                await callback.answer("😔 Ошибка: сообщение недоступно", show_alert=True)
                return
            
            # Отправляем новое сообщение для розыгрыша
            new_message = await callback.message.answer("🎯 Начинаем розыгрыш...")
            
            # Запускаем розыгрыш
            prize = await spin_roulette(new_message, config["prizes"], config["review_link"])
            await save_user_spin(user_id)
            
            log_user_action(user_id, "won_prize", f"Prize: {prize['name']}")
            
        except Exception as e:
            log_error(e, f"spin_roulette_callback for user {callback.from_user.id if callback.from_user else 'Unknown'}")
            await callback.answer("😔 Произошла ошибка. Попробуйте позже.", show_alert=True)

    dp.include_router(router)
