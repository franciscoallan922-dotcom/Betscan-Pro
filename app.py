import streamlit as st
import requests
import os

# 🔐 API KEY
API_KEY = os.getenv("RAPIDAPI_KEY")

if not API_KEY:
    st.error("❌ API KEY não configurada")
    st.stop()

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

st.set_page_config(page_title="BetScan PRO", page_icon="⚽")

st.title("⚽ BetScan PRO")
st.caption("Scanner automático de jogos")

# 🔍 DEBUG (pode desligar depois)
DEBUG = False

# 🔄 BUSCAR JOGOS
@st.cache_data(ttl=300)
def buscar_jogos():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    try:
        res = requests.get(url, headers=HEADERS, params={"next": 20})

        if DEBUG:
            st.write("STATUS:", res.status_code)

        if res.status_code != 200:
            return []

        data = res.json()

        jogos = []

        for j in data.get("response", []):
            jogos.append({
                "home": j["teams"]["home"]["name"],
                "away": j["teams"]["away"]["name"],
                "home_id": j["teams"]["home"]["id"],
                "away_id": j["teams"]["away"]["id"]
            })

        return jogos

    except Exception as e:
        if DEBUG:
            st.write("ERRO:", e)
        return []

# 📊 ÚLTIMOS JOGOS
@st.cache_data(ttl=300)
def ultimos_jogos(team_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    try:
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

    except:
        return 0

# 🧠 SCORE
def calcular_score(media):
    if media >= 3:
        return 3
    elif media >= 2.5:
        return 2
    elif media >= 1.5:
        return 1
    else:
        return 0

# 🚀 BOTÃO
if st.button("🔍 Escanear Jogos do Dia"):

    jogos = buscar_jogos()

    # 🔥 Fallback (se API falhar)
    if not jogos:
        st.warning("⚠️ API não retornou jogos. Usando fallback...")

        jogos = [
            {"home": "Time A", "away": "Time B", "home_id": 33, "away_id": 34},
            {"home": "Time C", "away": "Time D", "home_id": 40, "away_id": 50},
        ]

    resultados = []
    progress = st.progress(0)

    for i, jogo in enumerate(jogos):

        g_home = ultimos_jogos(jogo["home_id"])
        g_away = ultimos_jogos(jogo["away_id"])

        media = (g_home + g_away) / 2
        score = calcular_score(media)

        resultados.append({
            "jogo": f"{jogo['home']} x {jogo['away']}",
            "media": media,
            "score": score
        })

        progress.progress((i + 1) / len(jogos))

    resultados = sorted(resultados, key=lambda x: x["score"], reverse=True)

    st.markdown("---")
    st.subheader("🔥 Melhores jogos")

    for r in resultados[:5]:

        if r["score"] == 3:
            st.success(f"🔥 {r['jogo']}")
            st.write(f"⚽ Média: {r['media']:.2f}")
            st.write("🎯 Over 2.5 gols")

        elif r["score"] == 2:
            st.warning(f"⚠️ {r['jogo']}")
            st.write(f"⚽ Média: {r['media']:.2f}")
            st.write("🎯 Over 1.5 gols")

        else:
            st.info(f"{r['jogo']}")
            st.write(f"⚽ Média: {r['media']:.2f}")
            st.write("⚖️ Jogo neutro")
