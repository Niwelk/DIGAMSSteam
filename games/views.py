import requests
from django.conf import settings
from django.shortcuts import render


def index(request):
    query = request.GET.get('query', '')
    games = []
    if query:
        search_url = f"https://store.steampowered.com/api/storesearch/?term={query}&l=russian&cc=RU"
        try:
            response = requests.get(search_url).json()
            if response and response.get('items'):
                games = response['items']
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

        achievements.sort(key=lambda x: x['difficulty_score'], reverse=True)

    except Exception as e:
        print(f"Ошибка в цикле: {e}")

    return render(request, 'games/achievements.html', {
        'achievements': achievements,
        'game': {'name': game_name, 'steam_id': game_id}
    })


def test_api(request): return render(request, 'games/index.html')


def get_search_history(request): return render(request, 'games/index.html')


def get_price(request, game_id): return render(request, 'games/index.html')


def get_price_history(request, game_id): return render(request, 'games/index.html')


def register(request): return render(request, 'games/index.html')


def login_view(request): return render(request, 'games/index.html')