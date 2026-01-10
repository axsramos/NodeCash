import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        /* Fundo principal e Sidebar */
        .stApp {
            background-color: #0E1117;
            color: #FFFFFF;
        }
        
        /* Estilização dos Cards de Métrica */
        [data-testid="stMetricValue"] {
            color: #39FF14; /* Neon Green */
            font-family: 'Courier New', monospace;
        }

        /* Títulos e Headers */
        h1, h2, h3 {
            color: #F0F2F6;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        /* Estilo para a Barra Lateral */
        section[data-testid="stSidebar"] {
            background-color: #1A1C24;
            border-right: 1px solid #39FF14;
        }
        </style>
    """, unsafe_allow_html=True)