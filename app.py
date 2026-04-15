import streamlit as st
import requests
from datetime import datetime

API_KEY = st.secrets["RAPIDAPI_KEY"]

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

st.set_page_config(page_title="BetScan Scanner", page_icon="⚽")

st.title("⚽ BetScan Scanner")
st.caption("Radar automático dos melhores jogos do dia")

# 🔄 Buscar jogos
@st.cache_data(ttl=300)
def buscar_jogos():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    hoje = datetime.now().strftime("%Y-%m-%d")
    
    res = requests.get(url, headers=HEADERS, params={"date": hoje}).json()
    
    jogos = []
    
    for j in res["response"]:
        jogos.append({
            "home": j["teams"]["home"]["name"],
            "away": j["teams"]["away"]["name"],
            "home_id": j["teams"]["home"]["id"],
            "away_id": j["teams"]["away"]["id"]
        })
    
    return jogos

# 🔄 Últimos jogos
@st.cache_data(ttl=300)
def ultimos_jogos(team_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    res = requests.get(
        url,
        headers=HEADERS,
        params={"team": team_id, "last": 5}
    ).json()
    
    gols = []
    
    for j in res["response"]:
        g = (j["goals"]["home"] or 0) + (j["goals"]["away"] or 0)
        gols.append(g)
    
    media_gols = sum(gols) / len(gols) if gols else 0
    
    return media_gols

# 🧠 Score do jogo
def calcular_score(media_gols):
    score = 0
    
    if media_gols >= 3:
        score += 3
    elif media_gols >= 2.5:
        score += 2
    elif media_gols >= 1.5:
        score += 1
    
    return score

# 🚀 SCANNER
if st.button("🔍 Escanear Jogos do Dia"):
    
    jogos = buscar_jogos()
    
    if not jogos:
        st.error("❌ Nenhum jogo encontrado")
        st.stop()
    
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
    
    # ordenar
    resultados = sorted(resultados, key=lambda x: x["score"], reverse=True)
    
    st.markdown("---")
    st.subheader("🔥 Melhores jogos do dia")
    
    for r in resultados[:5]:  # TOP 5
        
        if r["score"] >= 3:
            st.success(f"🔥 {r['jogo']}")
            st.write(f"⚽ Média de gols: {r['media']:.2f}")
            st.write("Sugestão: Over 2.5 gols")
        
        elif r["score"] == 2:
            st.warning(f"⚠️ {r['jogo']}")
            st.write(f"⚽ Média: {r['media']:.2f}")
            st.write("Sugestão: Over 1.5 gols")
