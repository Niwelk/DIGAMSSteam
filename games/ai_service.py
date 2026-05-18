import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


def analyze_game(game_name, description, achievements_count):
    prompt = f"""
Ты игровой аналитик.

Игра: {game_name}
Описание: {description}
Достижения: {achievements_count}

Сделай:
- краткий обзор
- сложность
- стоит ли играть
- кому зайдёт

Пиши по-русски.
"""

    try:
        # ВАЖНО: сначала узнаём доступные модели
        models = [m.name for m in genai.list_models()]

        # выбираем первую подходящую автоматически
        model_name = None

        for m in models:
            if "flash" in m:
                model_name = m
                break

        if not model_name:
            return f"Нет доступных моделей Gemini: {models}"

        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        return f"AI временно недоступен: {str(e)}"