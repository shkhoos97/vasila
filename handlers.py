import io
import logging
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ContentType
from services import ai_service
from keyboards import get_analysis_keyboard

logger = logging.getLogger(__name__)
router = Router()

# Простое хранилище последнего анализа в памяти (user_id -> last_analysis_text)
user_last_context = {}

@router.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        "🔥 **Приветствую, брат! На связи твой персональный Пикап-Мастер и НЛП-наставник.**\n\n"
        "Я здесь для того, чтобы ты перестал сливать переписки, вышел из френдзоны, научился "
        "читать женщин как открытую книгу и завоевал сердце той самой.\n\n"
        "⚡ **Что я умею:**\n"
        "1. 📸 **Анализировать скриншоты диалогов** (из Telegram, Tinder, WhatsApp, VK, Instagram).\n"
        "2. ✍️ **Разбирать текст переписки** — просто скопируй диалог сюда.\n"
        "3. 🧠 **Считывать скрытый подтекст** через призму психологии и НЛП: интерес, проверки (шит-тесты), баланс значимости.\n"
        "4. 🎯 **Давать 3 бронебойных варианта ответа** (игривый, уверенный, интригующий).\n"
        "5. ☕ **Выводить на свидание** без давления и отказов.\n\n"
        "👉 **Как начать:** Просто отправь мне скриншот вашей переписки или перешли/вставь сообщения!"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "💡 **Инструкция по использованию бота:**\n\n"
        "• **Отправка скриншота**: Прикрепи изображение экрана с перепиской. В подписи к фото (caption) можешь уточнить: "
        "«Кто она, где познакомились, сколько общаетесь, какая цель». Это повысит точность анализа!\n\n"
        "• **Отправка текста**: Просто напиши или скопируй реплики, например:\n"
        "  _Она: Привет, ну что, как дела?_\n"
        "  _Я: Привет, работаю, ты как?_\n"
        "  _Она: Понятно..._\n\n"
        "• **Кнопки под разбором**: Используй интерактивные кнопки, чтобы запросить ещё варианты, спланировать свидание или составить психологический портрет."
    )
    await message.answer(help_text, parse_mode="Markdown")

@router.message(Command("rules"))
async def cmd_rules(message: Message):
    rules_text = (
        "👑 **Золотые правила переписки от Мастера:**\n\n"
        "1. **Фрейм ценности**: Твое внимание ценно. Никогда не строчи простыни текста в ответ на односложные ответы.\n"
        "2. **Правило паузы**: Не отвечай мгновенно, если она отвечала 3 часа. Держи баланс динамики (Pacing).\n"
        "3. **Никаких оправданий**: Мужчина не защищается. Любую подколку мы рефреймим в шутку или флирт.\n"
        "4. **Цель переписки — реальная встреча**: Не превращайся в подружку по переписке или бесплатного клоуна."
    )
    await message.answer(rules_text, parse_mode="Markdown")

@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    user_id = message.from_user.id
    processing_msg = await message.answer("🔍 *Мастер изучает скриншот диалога и калибрует скрытые сигналы...*", parse_mode="Markdown")

    try:
        # Берём фото наибольшего разрешения
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        photo_bytes_io = io.BytesIO()
        await bot.download_file(file_info.file_path, destination=photo_bytes_io)
        image_bytes = photo_bytes_io.getvalue()

        user_comment = message.caption
        analysis = await ai_service.analyze_chat_image(image_bytes, user_comment)

        user_last_context[user_id] = analysis

        await processing_msg.delete()
        await message.answer(analysis, reply_markup=get_analysis_keyboard())
    except Exception as e:
        logger.error(f"Error handling photo: {e}")
        await processing_msg.edit_text(f"⚠️ Ошибка обработки скриншота: {e}")

@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message):
    user_id = message.from_user.id
    processing_msg = await message.answer("🧠 *Мастер анализирует переписку и подбирает ключи к её психологии...*", parse_mode="Markdown")

    try:
        chat_text = message.text
        analysis = await ai_service.analyze_chat_text(chat_text)

        user_last_context[user_id] = analysis

        await processing_msg.delete()
        await message.answer(analysis, reply_markup=get_analysis_keyboard())
    except Exception as e:
        logger.error(f"Error handling text: {e}")
        await processing_msg.edit_text(f"⚠️ Ошибка анализа: {e}")

@router.callback_query(F.data.startswith("action:"))
async def handle_action_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    action_type = callback.data.split(":")[1]

    last_analysis = user_last_context.get(user_id)
    if not last_analysis:
        await callback.answer("Сначала отправь переписку или скриншот для анализа!", show_alert=True)
        return

    await callback.answer("Генерирую...")
    wait_msg = await callback.message.reply("⚡ *Мастер формулирует специальное решение...*", parse_mode="Markdown")

    follow_up_result = await ai_service.get_follow_up(last_analysis, action_type)
    await wait_msg.delete()
    await callback.message.reply(follow_up_result)
