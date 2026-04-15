import streamlit as st
import requests
import os

API_KEY = os.getenv("RAPIDAPI_KEY")

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

st.title("⚽ BetScan PRO")
st.caption("Análise de jogos + necessidade de vitória")

# 🔄 BUSCAR JOGOS
@st.cache_data(ttl=300)
def buscar_jogos():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    res = requests.get(url, headers=HEADERS, params={"next": 10})

    if res.status_code != 200:
        return []

    return res.json().get("response", [])

# 📊 ÚLTIMOS JOGOS
@st.cache_data(ttl=300)
def ultimos_jogos(team_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    res = requests.get(
        url,
        headers=HEADERS,
        params={"team": team_id, "last": 5}
    )

    if res.status_code != 200:
        return 0

    gols = []

    for j in res.json().get("response", []):
        g = (j["goals"]["home"] or 0) + (j["goals"]["away"] or 0)
        gols.append(g)

    return sum(gols) / len(gols) if gols else 0

# 🏆 CLASSIFICAÇÃO
@st.cache_data(ttl=300)
def tabela(league_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/standings"

    res = requests.get(
        url,
        headers=HEADERS,
        params={"league": league_id, "season": 2024}
    )

    if res.status_code != 200:
        return {}

    tabela = {}

    try:
        for t in res.json()["response"][0]["league"]["standings"][0]:
            tabela[t["team"]["id"]] = t["rank"]
    except:
        return {}

    return tabela

# 🧠 ANÁLISE
def analisar(media, pos_home, pos_away):

    necessidade = ""

    if pos_home and pos_away:
        if pos_home > pos_away:
            necessidade = "🔥 Casa precisa vencer"
        elif pos_away > pos_home:
            necessidade = "🔥 Visitante precisa vencer"

    if media >= 3:
        sugestao = "🔥 Over 2.5 gols"
    elif media >= 2:
        sugestao = "⚠️ Over 1.5 gols"
    else:
        sugestao = "⚖️ Jogo fechado"

    return necessidade, sugestao

# 🚀 EXECUÇÃO
if st.button("🔍 Analisar Jogos"):

    jogos = buscar_jogos()

    if not jogos:
        st.error("❌ API não retornou jogos")
        st.stop()

    for j in jogos:

        home = j["teams"]["home"]["name"]
        away = j["teams"]["away"]["name"]

        home_id = j["teams"]["home"]["id"]
        away_id = j["teams"]["away"]["id"]

        league_id = j["league"]["id"]

        # dados
        media_home = ultimos_jogos(home_id)
        media_away = ultimos_jogos(away_id)

        media_total = (media_home + media_away) / 2

        tabela_liga = tabela(league_id)

        pos_home = tabela_liga.get(home_id)
        pos_away = tabela_liga.get(away_id)

        necessidade, sugestao = analisar(media_total, pos_home, pos_away)

        # UI
        st.markdown("---")
        st.subheader(f"{home} x {away}")

        st.write(f"⚽ Média de gols: {media_total:.2f}")

        if pos_home and pos_away:
            st.write(f"📊 Posição: {home} ({pos_home}) vs {away} ({pos_away})")

        if necessidade:
            st.warning(necessidade)

        st.success(sugestao)
