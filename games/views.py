import requests
from django.conf import settings
from django.shortcuts import render

from .ai_service import analyze_game
import requests
from django.shortcuts import render


def ai_analysis(request, game_id):
    url = "https://store.steampowered.com/api/appdetails/"
    params = {"appids": game_id, "l": "russian"}

    game_name = ""
    description = ""
    achievements_count = 0

    try:
        data = requests.get(url, params=params).json()
        game = data.get(str(game_id), {}).get("data", {})

        game_name = game.get("name", "Unknown")
        description = game.get("short_description", "No description")

        # achievements (если есть)
        achievements = game.get("achievements", {})
        achievements_count = achievements.get("total", 0)

    except Exception:
        pass

    analysis = analyze_game(game_name, description, achievements_count)

    return render(request, "games/ai.html", {
        "game_name": game_name,
        "analysis": analysis
    })

def index(request):

    query = request.GET.get('query', '').strip()

    games = []

    if query:

        search_url = (
            "https://store.steampowered.com/api/storesearch/"
        )

        params = {
            "term": query,
            "l": "english",
            "cc": "US"
        }

        try:

            response = requests.get(
                search_url,
                params=params,
                timeout=10
            )

            data = response.json()

            if data and data.get('items'):

                raw_games = data['items']

                for game in raw_games:

                    image = (
                        game.get('tiny_image')
                        or game.get('large_capsule_image')
                        or game.get('image')
                        or ''
                    )

                    if image and image.startswith('/'):

                        image = (
                            f"https://store.steampowered.com{image}"
                        )

                    games.append({
                        'id': game.get('id'),
                        'name': game.get('name'),
                        'image': image,
                    })

        except Exception as e:

            print(f"Ошибка поиска: {e}")

    return render(
        request,
        'games/index.html',
        {
            'games': games,
            'query': query
        }
    )

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

    achievements = []

    game_name = f"Game {game_id}"

    try:

        rarity_url = (
            "https://api.steampowered.com/"
            "ISteamUserStats/"
            "GetGlobalAchievementPercentagesForApp/v0002/"
        )

        schema_url = (
            "https://api.steampowered.com/"
            "ISteamUserStats/"
            "GetSchemaForGame/v2/"
        )

        rarity_response = requests.get(
            rarity_url,
            params={
                "gameid": game_id
            },
            timeout=10
        )

        schema_response = requests.get(
            schema_url,
            params={
                "key": api_key,
                "appid": game_id
            },
            timeout=10
        )

        rarity_data = rarity_response.json()

        schema_data = schema_response.json()

        rarity_list = (
            rarity_data
            .get('achievementpercentages', {})
            .get('achievements', [])
        )

        game_data = schema_data.get('game', {})

        game_name = game_data.get(
            'gameName',
            game_name
        )

        schema_list = (
            game_data
            .get('availableGameStats', {})
            .get('achievements', [])
        )

        schema_dict = {
            ach['name']: ach
            for ach in schema_list
        }

        for ach in rarity_list:

            api_name = ach.get('name')

            rarity = float(
                ach.get('percent', 0)
            )

            schema = schema_dict.get(api_name)

            if not schema:
                continue

            difficulty = round(
                10 - (rarity / 10),
                2
            )

            difficulty = max(
                0.1,
                min(10.0, difficulty)
            )

            achievements.append({

                'name': schema.get(
                    'displayName',
                    api_name
                ),

                'description': schema.get(
                    'description',
                    'Hidden achievement'
                ),

                'icon': schema.get(
                    'icon',
                    ''
                ),

                'rarity': round(rarity, 1),

                'difficulty_score': difficulty
            })

    except Exception as e:

        print(f"Achievement API error: {e}")

    filter_type = request.GET.get(
        'filter',
        'all'
    )

    if filter_type == 'rare':

        achievements = [
            a for a in achievements
            if a['difficulty_score'] >= 7
        ]

    elif filter_type == 'popular':

        achievements = [
            a for a in achievements
            if a['difficulty_score'] <= 3
        ]

    sort_by = request.GET.get(
        'sort',
        'difficulty'
    )

    if sort_by == 'difficulty':

        achievements.sort(
            key=lambda x: x['difficulty_score'],
            reverse=True
        )

    elif sort_by == 'rarity':

        achievements.sort(
            key=lambda x: x['rarity']
        )

    elif sort_by == 'name':

        achievements.sort(
            key=lambda x: x['name']
        )

    return render(
        request,
        'games/achievements.html',
        {
            'achievements': achievements,
            'game': {
                'name': game_name,
                'steam_id': game_id
            },
            'current_filter': filter_type,
            'current_sort': sort_by,
        }
    )


# остальные заглушки (test_api, get_search_history, register и т.д.) можно оставить как есть
def test_api(request): return render(request, 'games/index.html')
def get_search_history(request): return render(request, 'games/index.html')
def get_price(request, game_id): return render(request, 'games/index.html')
def get_price_history(request, game_id): return render(request, 'games/index.html')
def register(request): return render(request, 'games/index.html')
def login_view(request): return render(request, 'games/index.html')