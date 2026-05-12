import streamlit as st
import requests

st.set_page_config(page_title="Steam Achievement Intelligence", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #1b2838; }
    .stTextInput>div>div>input { background-color: #2a475e; color: white; border: none; }

    .achievement-card {
        background-color: #171a21;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #66c0f4;
        transition: 0.3s;
    }
    .achievement-card:hover {
        background-color: #2a475e;
    }
    .game-title { color: #66c0f4; font-size: 24px; font-weight: bold; }
    .desc-text { color: #acb2b8; font-size: 14px; margin-top: 5px; }
    .badge {
        background: #A349A4;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        color: white;
    }
    .rarity-text { color: #8f98a0; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000/api"

st.title("🏆 Steam Achievement Intelligence")
st.markdown("---")

query = st.text_input("🔍 Поиск игры по названию", placeholder="Введите название (например, CS2)")

if query:
    try:
        search_res = requests.get(f"{API_URL}/search/", params={"query": query})
        if search_res.status_code == 200:
            games = search_res.json().get("games", [])

            if not games:
                st.info("Игры не найдены. Попробуйте другое название.")
            else:
                st.subheader("Результаты поиска")
                for game in games:
                    col_img, col_info = st.columns([1, 5])
                    with col_img:
                        st.image(game['image'], width=150)
                    with col_info:
                        st.markdown(f"<div class='game-title'>{game['name']}</div>", unsafe_allow_html=True)
                        st.write(f"Steam ID: {game['id']}")
                        if st.button(f"Выбрать {game['name']}", key=f"btn_{game['id']}"):
                            st.session_state.selected_game = game['id']
                            st.session_state.game_name = game['name']
        else:
            st.error("Ошибка API бэкенда")
    except Exception as e:
        st.error(f"Ошибка подключения: {e}")

if 'selected_game' in st.session_state:
    st.markdown("---")
    st.header(f"Анализ достижений: {st.session_state.game_name}")

    with st.spinner("Синхронизация данных со Steam..."):
        res = requests.get(f"{API_URL}/game/{st.session_state.selected_game}/achievements/")
        if res.status_code == 200:
            achievements = res.json().get("achievements", [])

            achievements = sorted(achievements, key=lambda x: x['difficulty_score'], reverse=True)

            for ach in achievements:
                st.markdown(f"""
                    <div class="achievement-card">
                        <div style="display: flex; align-items: flex-start;">
                            <img src="{ach['icon']}" style="width: 54px; height: 54px; margin-right: 15px; border-radius: 3px;">
                            <div style="flex-grow: 1;">
                                <div style="display: flex; justify-content: space-between;">
                                    <strong style="color: #ffffff; font-size: 16px;">{ach['name']}</strong>
                                    <span class="badge">Сложность: {ach['difficulty_score']}/10</span>
                                </div>
                                <div class="desc-text">{ach['description']}</div>
                                <div style="margin-top: 8px; display: flex; justify-content: space-between;">
                                    <span class="rarity-text">Получили: {ach['rarity']}% игроков</span>
                                    <span style="color: #57cbde; font-size: 12px; font-weight: bold;">{ach.get('category', '').upper()}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Не удалось получить данные о достижениях.")