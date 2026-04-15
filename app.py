import streamlit as st
import requests
from datetime import datetime
import os

# 🔐 API KEY (Railway)
API_KEY = os.getenv("RAPIDAPI_KEY")

if not API_KEY:
    st.error("❌ API KEY não configurada")
    st.stop()

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# 🎨 CONFIG
st.set_page_config(page_title="BetScan PRO", page_icon="⚽", layout="wide")

st.title("⚽ BetScan PRO")
st.caption("Scanner automático (AO VIVO + PRÓXIMOS JOGOS)")

# 🔴 JOGOS AO VIVO
@st.cache_data(ttl=60)
def jogos_ao_vivo():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    try:
        res = requests.get(url, headers=HEADERS, params={"live": "all"})
        
        if res.status_code != 200:
            return []
        
        return res.json().get("response", [])
    
    except:
        return []

# 🔄 PRÓXIMOS JOGOS
@st.cache_data(ttl=300)
def proximos_jogos():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    try:
        res = requests.get(url, headers=HEADERS, params={"next": 30})
        
        if res.status_code != 200:
            return []
        
        return res.json().get("response", [])
    
    except:
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
    score = 0
    
    if media >= 3:
        score += 3
    elif media >= 2.5:
        score += 2
    elif media >= 1.5:
        score += 1
    
    return score

# 🚀 BOTÃO
if st.button("🔍 Escanear Jogos"):
    
    jogos = []

    # 🔴 ao vivo primeiro
    for j in jogos_ao_vivo():
        jogos.append(j)

    # 🔄 depois próximos
    for j in proximos_jogos():
        jogos.append(j)

    if not jogos:
        st.error("❌ Nenhum jogo encontrado")
        st.stop()

    resultados = []
    progress = st.progress(0)

    for i, j in enumerate(jogos):
        
        home = j["teams"]["home"]["name"]
        away = j["teams"]["away"]["name"]
        home_id = j["teams"]["home"]["id"]
        away_id = j["teams"]["away"]["id"]

        g_home = ultimos_jogos(home_id)
        g_away = ultimos_jogos(away_id)

        media = (g_home + g_away) / 2
        score = calcular_score(media)

        resultados.append({
            "jogo": f"{home} x {away}",
            "media": media,
            "score": score
        })

        progress.progress((i + 1) / len(jogos))

    # ordenar melhores
    resultados = sorted(resultados, key=lambda x: x["score"], reverse=True)

    st.markdown("---")
    st.subheader("🔥 MELHORES JOGOS AGORA")

    for r in resultados[:7]:
        
        if r["score"] >= 3:
            st.success(f"🔥 {r['jogo']}")
            st.write(f"⚽ Média: {r['media']:.2f}")
            st.write("🎯 Sugestão: Over 2.5 gols")

        elif r["score"] == 2:
            st.warning(f"⚠️ {r['jogo']}")
            st.write(f"⚽ Média: {r['media']:.2f}")
            st.write("🎯 Sugestão: Over 1.5 gols")

        else:
            st.info(f"{r['jogo']}")
            st.write(f"⚽ Média: {r['media']:.2f}")
            st.write("⚖️ Jogo equilibrado")

# 📌 SIDEBAR
st.sidebar.info("Scanner inteligente ativo 🚀")
