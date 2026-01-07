import streamlit as st
import pandas as pd

st.title("Nodecash Dashboard 🍪")

# Exemplo de monitoramento de Peers
st.subheader("Peers Ativos")
peers = {"Endereço": ["192.168.1.10", "45.79.10.12"], "Último Sinal": ["14:20", "14:25"]}
st.table(pd.DataFrame(peers))

# Gráfico de transações (simulado)
st.subheader("Tráfego de Dados")
st.line_chart([10, 25, 15, 40, 30])