import base64
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from config import settings
from prompts import (
    PICKUP_MASTER_SYSTEM_PROMPT,
    EXTRA_OPTIONS_PROMPT,
    DATE_INVITE_PROMPT,
    PSYCHOLOGY_BREAKDOWN_PROMPT
)

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        client_kwargs: Dict[str, Any] = {
            "api_key": settings.openai_api_key or "dummy_key"
        }
        if settings.openai_base_url:
            client_kwargs["base_url"] = settings.openai_base_url
        self.client = AsyncOpenAI(**client_kwargs)
        self.model = settings.openai_model

    async def analyze_chat_text(self, chat_text: str, user_comment: Optional[str] = None) -> str:
        """Анализирует текстовую переписку."""
        user_message_content = f"Вот переписка с девушкой:\n\n\"\"\"\n{chat_text}\n\"\"\""
        if user_comment:
            user_message_content += f"\n\nДополнительный комментарий / вопрос от меня:\n{user_comment}"

        messages = [
            {"role": "system", "content": PICKUP_MASTER_SYSTEM_PROMPT},
            {"role": "user", "content": user_message_content}
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.75,
                max_tokens=1500
            )
            return response.choices[0].message.content or "Не удалось сформировать ответ. Попробуйте еще раз."
        except Exception as e:
            logger.error(f"Error in analyze_chat_text: {e}")
            return f"⚠️ Ошибка при обращении к ИИ: {e}\nУбедитесь, что указан корректный OPENAI_API_KEY в файле .env."

    async def analyze_chat_image(self, image_bytes: bytes, user_comment: Optional[str] = None) -> str:
        """Анализирует скриншот переписки с помощью мультимодальной модели."""
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{base64_image}"

        text_prompt = "Внимательно прочитай переписку на этом скриншоте. Распознай реплики собеседников и проведи экспертный разбор как Мастер Соблазнения и НЛП по инструкции."
        if user_comment:
            text_prompt += f"\n\nКонтекст от пользователя:\n{user_comment}"

        messages = [
            {"role": "system", "content": PICKUP_MASTER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url,
                            "detail": "high"
                        }
                    }
                ]
            }
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.75,
                max_tokens=1500
            )
            return response.choices[0].message.content or "Не удалось проанализировать скриншот."
        except Exception as e:
            logger.error(f"Error in analyze_chat_image: {e}")
            return f"⚠️ Ошибка при анализе изображения: {e}\nПроверьте настройки API и модель в .env."

    async def get_follow_up(self, previous_context: str, action_type: str) -> str:
        """Генерирует дополнительные варианты или глубокий психологический разбор на основе предыдущего анализа."""
        prompt_map = {
            "more_options": EXTRA_OPTIONS_PROMPT,
            "invite_date": DATE_INVITE_PROMPT,
            "psychology": PSYCHOLOGY_BREAKDOWN_PROMPT
        }
        specific_prompt = prompt_map.get(action_type, EXTRA_OPTIONS_PROMPT)

        messages = [
            {"role": "system", "content": PICKUP_MASTER_SYSTEM_PROMPT},
            {"role": "assistant", "content": previous_context},
            {"role": "user", "content": specific_prompt}
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.75,
                max_tokens=1200
            )
            return response.choices[0].message.content or "Не удалось сгенерировать ответ."
        except Exception as e:
            logger.error(f"Error in get_follow_up: {e}")
            return f"⚠️ Ошибка генерации: {e}"

ai_service = AIService()
