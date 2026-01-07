import streamlit as st
import pandas as pd
import plotly.express as px
import json
import time
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# --- 1. CONFIGURAÇÕES E CONSTANTES GLOBAIS ---

def get_seeds_from_env():
    """Busca as sementes no .env na raiz do projeto"""
    base_path = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=base_path / ".env")
    seeds_raw = os.getenv("SEEDS", "")
    return [s.strip() for s in seeds_raw.split(",")] if seeds_raw else []

# Carregamento único na inicialização do módulo
SEEDS = get_seeds_from_env()

def get_peers_path():
    """Caminho absoluto para o peers.json"""
    return Path(__file__).resolve().parents[1] / "data" / "system" / "peers.json"

# --- 2. LÓGICA DE BACKEND (CORE INTERACTION) ---

def load_peers():
    """Lê o dicionário de peers e categoriza para o Dashboard"""
    file_path = get_peers_path()
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [
                    {
                        "Endereço": k, 
                        "Visto em": datetime.fromtimestamp(v).strftime('%H:%M:%S'),
                        "Tipo": "Semente" if k in SEEDS else ("Local" if "127.0.0.1" in k else "Externo")
                    } for k, v in data.items()
                ]
        except: return []
    return []

def run_peer_gc(timeout=30):
    """Garbage Collector: Remove inativos, mas ignora SEEDS"""
    file_path = get_peers_path()
    if not file_path.exists(): return 0
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        agora = time.time()
        # Regra: Mantém se for recente OU se for uma semente protegida
        dados_limpos = {k: v for k, v in data.items() if (agora - v < timeout) or (k in SEEDS)}
        removidos = len(data) - len(dados_limpos)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dados_limpos, f, indent=4)
        return removidos
    except Exception as e: return str(e)

# --- 3. INTERFACE (UI/UX) ---

def main():
    st.set_page_config(page_title="Nodecash Monitor", page_icon="🍪", layout="wide")
    st.title("Nodecash Dashboard 🍪")

    peers_list = load_peers()

    # Sidebar: Ações do Sistema
    with st.sidebar:
        st.header("⚙️ Gestão do Nó")
        if st.button("Executar Peer GC (Limpeza)"):
            res = run_peer_gc()
            if isinstance(res, int):
                st.sidebar.success(f"Limpeza OK: {res} removidos.")
                time.sleep(1)
                st.rerun()
            else: st.sidebar.error(res)
        
        st.divider()
        st.caption(f"Sementes no .env: {len(SEEDS)}")

    # Layout Principal
    col_metrics, col_chart = st.columns([1, 2])
    
    with col_metrics:
        st.metric("Total de Nodes", len(peers_list))
        st.write("Distribuição da Rede:")
        # Pequeno resumo textual
        for t in ["Semente", "Local", "Externo"]:
            count = sum(1 for p in peers_list if p['Tipo'] == t)
            st.write(f"- {t}: **{count}**")

    with col_chart:
        if peers_list:
            df = pd.DataFrame(peers_list)
            fig = px.pie(df, names='Tipo', hole=0.5, 
                         color_discrete_map={'Semente':'#FF4B4B', 'Local':'#F0B90B', 'Externo':'#EAECEF'})
            fig.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=280, 
                              paper_bgcolor='rgba(0,0,0,0)', font_color="#EAECEF")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Nodes Conectados (Tempo Real)")
    if peers_list:
        st.dataframe(pd.DataFrame(peers_list), use_container_width=True)
    else:
        st.info("Nenhuma bolacha... digo, node encontrado! Verifique a rede.")

if __name__ == "__main__":
    main()