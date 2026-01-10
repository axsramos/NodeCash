import streamlit as st
from utils import data_bridge
import pandas as pd
import numpy as np
import random

def render(node_id):
    # Busca dados específicos do nó selecionado
    data = data_bridge.get_node_status(node_id)
    
    st.title(f"🛠️ Detalhes Técnicos: Node {node_id}")
    
    # Linha 1: Status e Identificação
    col1, col2, col3, col4 = st.columns([1,1,1,2])
    col1.metric("Status", data['status'])
    col2.metric("Uptime", data['uptime'])
    col3.metric("Peers", data['peers'])
    col4.info(f"**Last Ping:** {data['last_ping']} | **Localização:** América do Sul")

    st.markdown("---")

    # Linha 2: Hardware & Performance
    st.subheader("🖥️ Consumo de Recursos")
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("**Uso de CPU & RAM (%)**")
        # Simulando dados de hardware
        chart_data = pd.DataFrame(
            np.random.randn(20, 2),
            columns=['CPU', 'RAM']
        )
        st.line_chart(chart_data)
        
    with c2:
        st.write("**Latência de Rede (ms)**")
        latency_history = [int(data['latencia'].replace('ms','')) + random.randint(-5, 5) for _ in range(20)]
        st.area_chart(latency_history)

    # Linha 3: Logs e Eventos do Sistema
    st.subheader("📜 System Logs (Real-time)")
    
    log_entries = [
        f"[{data['last_ping']}] INFO: Connection established with peer 192.168.1.45",
        f"[{data['last_ping']}] SUCCESS: Block #842,102 validated by {node_id}",
        f"[{data['last_ping']}] WARN: High memory usage detected in worker_01",
        f"[{data['last_ping']}] DEBUG: Heartbeat sent to main.py"
    ]
    
    # Simulação de um console de log
    st.code("\n".join(log_entries), language="bash")

    # Botão de Ação (Manutenção)
    if st.button(f"Reiniciar Node {node_id}"):
        st.warning(f"Comando de reinicialização enviado para o backend (main.py) do Node {node_id}...")