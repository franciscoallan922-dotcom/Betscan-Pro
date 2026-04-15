import streamlit as st
import requests
import os

API_KEY = os.getenv("RAPIDAPI_KEY")

if not API_KEY:
    st.error("❌ API KEY não configurada")
    st.stop()

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

st.title("⚽ BetScan PRO")
st.caption("Scanner profissional de jogos")

# 🔥 LIGAS QUE SEMPRE TEM JOGO
LEAGUES = [39, 140, 78, 135, 61]  
# Inglaterra, Espanha, Alemanha, Itália, França

# 🔄 BUSCAR JOGOS REAIS
@st.cache_data(ttl=300)
def buscar_jogos():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    jogos = []

    for liga in LEAGUES:
        res = requests.get(
            url,
            headers=HEADERS,
            params={
                "league": liga,
                "season": 2024,
                "next": 5,
                "timezone": "America/Sao_Paulo"
            }
        )

        if res.status_code != 200:
            continue

        data = res.json()

        for j in data.get("response", []):
            jogos.append({
                "home": j["teams"]["home"]["name"],
                "away": j["teams"]["away"]["name"],
                "home_id": j["teams"]["home"]["id"],
                "away_id": j["teams"]["away"]["id"]
            })

    return jogos

# 📊 ÚLTIMOS JOGOS
def ultimos_jogos(team_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    res = requests.get(
        url,
        headers=HEADERS,
        params={"team": team_id, "last": 5}
    )

    if res.status_code != 200:
        return 0

    data = res.json()

    gols = []

    for j in data.get("response", []):
        g = (j["goals"]["home"] or 0) + (j["goals"]["away"] or 0)
        gols.append(g)

    return sum(gols) / len(gols) if gols else 0

# 🧠 SCORE
def calcular_score(media):
    if media >= 3:
        return 3
    elif media >= 2.5:
        return 2
    elif media >= 1.5:
        return 1
    return 0

# 🚀 EXECUÇÃO
if st.button("🔍 Escanear Jogos"):

    jogos = buscar_jogos()

    if not jogos:
        st.error("❌ Nenhum jogo encontrado (API limitou ou sem jogos)")
        st.stop()

    resultados = []

    for jogo in jogos:

        g_home = ultimos_jogos(jogo["home_id"])
        g_away = ultimos_jogos(jogo["away_id"])

        media = (g_home + g_away) / 2
        score = calcular_score(media)

        resultados.append({
            "jogo": f"{jogo['home']} x {jogo['away']}",
            "media": media,
            "score": score
        })

    resultados = sorted(resultados, key=lambda x: x["score"], reverse=True)

    st.subheader("🔥 MELHORES JOGOS")

    for r in resultados[:7]:

        if r["score"] >= 3:
            st.success(f"🔥 {r['jogo']} → Over 2.5")
        elif r["score"] == 2:
            st.warning(f"⚠️ {r['jogo']} → Over 1.5")
        else:
            st.info(f"{r['jogo']} → neutro")
