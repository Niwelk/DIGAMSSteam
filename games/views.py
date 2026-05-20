import requests
from django.conf import settings
from django.shortcuts import render
from gigachat import GigaChat

def index(request):
    query = request.GET.get('query', '')
    games = []
    if query:
        # Дима, тут я короче использую английскую локаль по умолчанию, чтобы Steam находил Witcher 3 и Phasmophobia и некие другие игры, которые не находил, если хочешь можешь отрефакторить
        fallback_url = f"https://store.steampowered.com/api/storesearch/?term={query}&l=english&cc=US"
        try:
            res_json = requests.get(fallback_url).json()
            if res_json and res_json.get('items'):
                games = res_json['items']
        except Exception as e:
            print(f"Ошибка поиска: {e}")
    return render(request, 'games/index.html', {'games': games, 'query': query})


def game_detail(request, game_id):
    url = "https://store.steampowered.com/api/appdetails/"
    params = {"appids": game_id, "l": "russian"}
    game_data = {}
    try:
        response = requests.get(url, params=params).json()
        if response.get(str(game_id), {}).get("success"):
            raw_data = response[str(game_id)]["data"]
            game_data = {
                "steam_id": game_id,
                "name": raw_data.get("name"),
                "description": raw_data.get("short_description"),
                "image": raw_data.get("header_image"),
                "price": raw_data.get("price_overview", {}).get("final_formatted", "Бесплатно")
            }
    except Exception as e:
        print(f"Ошибка деталей: {e}")
    return render(request, 'games/game_detail.html', {'game': game_data})


def get_achievements(request, game_id):
    api_key = settings.STEAM_API_KEY
    url_rarity = f"http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={game_id}"
    url_schema = f"http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={api_key}&appid={game_id}"

    achievements = []
    game_name = f"Игра {game_id}"

    try:
        res_rarity = requests.get(url_rarity).json()
        res_schema = requests.get(url_schema).json()

        rarity_list = res_rarity.get('achievementpercentages', {}).get('achievements', [])
        game_metadata = res_schema.get('game', {})
        schema_list = game_metadata.get('availableGameStats', {}).get('achievements', [])
        game_name = game_metadata.get('gameName', game_name)

        schema_dict = {a['name']: a for a in schema_list}

        for item in rarity_list:
            api_name = item['name']
            percent = float(item.get('percent', 0))

            if api_name in schema_dict:
                data = schema_dict[api_name]
                difficulty = round(10 - (percent / 10), 2)
                if difficulty < 0.1: difficulty = 0.1

                achievements.append({
                    'name': data.get('displayName', api_name),
                    'description': data.get('description', 'Условие скрыто'),
                    'icon': data.get('icon', ''),
                    'rarity': round(percent, 1),
                    'difficulty_score': difficulty
                })

        current_filter = request.GET.get('filter', 'all')
        if current_filter == 'rare':
            achievements = [a for a in achievements if a['rarity'] <= 10]
        elif current_filter == 'popular':
            achievements = [a for a in achievements if a['rarity'] > 30]

        achievements.sort(key=lambda x: x['difficulty_score'], reverse=True)

    except Exception as e:
        print(f"Ошибка: {e}")
        current_filter = 'all'

    return render(request, 'games/achievements.html', {
        'achievements': achievements,
        'game': {'name': game_name, 'steam_id': game_id},
        'current_filter': current_filter
    })


def ai_analysis(request, game_id):
    api_key = settings.STEAM_API_KEY
    url_schema = f"http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={api_key}&appid={game_id}"

    game_name = f"Игра {game_id}"
    achievements_details = ""

    try:
        res_schema = requests.get(url_schema).json()
        game_metadata = res_schema.get('game', {})
        game_name = game_metadata.get('gameName', game_name)
        schema_list = game_metadata.get('availableGameStats', {}).get('achievements', [])

        if schema_list:
            ach_names = [a.get('displayName', '') for a in schema_list[:10] if a.get('displayName')]
            achievements_details = ", ".join(ach_names)
    except Exception as e:
        print(f"Ошибка получения данных Steam: {e}")

    try:
        prompt = (
            f"Ты — профессиональный геймер и аналитик. Сделай конкретный, краткий тактический обзор "
            f"и стратегический план для игры '{game_name}'. "
        )
        if achievements_details:
            prompt += f"В этой игре есть такие achievements: {achievements_details}. "

        prompt += (
            "Напиши ровно 3 главных совета, адаптированных под жанр игры (например, если это кооперативный хоррор "
            "как Phasmophobia — пиши про призраков, улики и команду; если RPG как Witcher — про квесты и прокачку). "
            "Избегай общих фраз. Форматируй ответ строго списками с эмодзи."
        )

        with GigaChat(credentials=settings.GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
            response = giga.chat(prompt)
            analysis = response.choices[0].message.content

    except Exception as e:
        print(f"Ошибка GigaChat: {e}")
        analysis = (
            f"🤖 *Сервер ИИ временно перегружен.*\n\n"
            f"Базовый план для **{game_name}**:\n"
            f"• Изучите специфику достижений во вкладке списков.\n"
            f"• Обратите внимание на скрытые трофеи (редкость менее 5%)."
        )

    return render(request, 'games/ai.html', {
        'game_name': game_name,
        'analysis': analysis,
        'game': {'steam_id': game_id, 'name': game_name}
    })