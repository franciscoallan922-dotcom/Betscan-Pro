import streamlit as st
import requests
from datetime import datetime
import os

# 🔐 CONFIG API
API_KEY = os.getenv("RAPIDAPI_KEY")

if not API_KEY:
    st.error("❌ API KEY não configurada no Railway")
    st.stop()

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# 🎨 CONFIG PAGE
st.set_page_config(page_title="BetScan PRO", page_icon="⚽", layout="wide")

st.title("⚽ BetScan PRO")
st.caption("Scanner automático dos melhores jogos do dia")

# 🔄 BUSCAR JOGOS DO DIA
@st.cache_data(ttl=300)
def buscar_jogos():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    hoje = datetime.now().strftime("%Y-%m-%d")
    
    try:
        res = requests.get(url, headers=HEADERS, params={"date": hoje})
        
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
    
    except:
        return []

# 🔄 ÚLTIMOS JOGOS (GOLS)
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

# 🧠 SCORE INTELIGENTE
def calcular_score(media_gols):
    score = 0
    
    if media_gols >= 3:
        score += 3
    elif media_gols >= 2.5:
        score += 2
    elif media_gols >= 1.5:
        score += 1
    
    return score

# 🚀 INTERFACE
if st.button("🔍 Escanear Jogos do Dia"):
    
    jogos = buscar_jogos()
    
    if not jogos:
        st.error("❌ Nenhum jogo encontrado hoje")
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
    
    # 🔥 ORDENAR MELHORES
    resultados = sorted(resultados, key=lambda x: x["score"], reverse=True)
    
    st.markdown("---")
    st.subheader("🔥 TOP Jogos do Dia")
    
    for r in resultados[:5]:
        
        if r["score"] >= 3:
            st.success(f"🔥 {r['jogo']}")
            st.write(f"⚽ Média de gols: {r['media']:.2f}")
            st.write("🎯 Sugestão: Over 2.5 gols")
        
        elif r["score"] == 2:
            st.warning(f"⚠️ {r['jogo']}")
            st.write(f"⚽ Média: {r['media']:.2f}")
            st.write("🎯 Sugestão: Over 1.5 gols")
        
        else:
            st.info(f"{r['jogo']}")
            st.write(f"⚽ Média: {r['media']:.2f}")
            st.write("⚠️ Jogo equilibrado")

# 📌 SIDEBAR
st.sidebar.info("Sistema automático de análise pré-jogo 🚀")
