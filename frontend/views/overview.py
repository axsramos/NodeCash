import streamlit as st
from utils import data_bridge

def render():
    st.title("🌐 Global Health Monitor")
    st.markdown("---")

    # 1. KPIs Globais (Resumo de tudo)
    col_g1, col_g2, col_g3 = st.columns(3)
    col_g1.metric("Total Nodes", "3", "Online")
    col_g2.metric("Total Cash (24h)", "R$ 450,20", "+12%")
    col_g3.metric("Network Uptime", "99.99%", "Stable")

    st.write("### Status por Região")
    
    # 2. Grid de Nodes (BR, SC, SP)
    nodes = ["BR", "SC", "SP"]
    cols = st.columns(len(nodes))

    for i, node_name in enumerate(nodes):
        with cols[i]:
            # Buscamos os dados reais (ou mockados) via bridge
            data = data_bridge.get_node_status(node_name)
            
            # Container estilizado para cada Node
            with st.container(border=True):
                st.subheader(f"📍 Node {node_name}")
                
                status_color = "🟢" if data['status'] == "Online" else "🔴"
                st.write(f"Status: {status_color} **{data['status']}**")
                
                st.caption(f"Latência: {data['latencia']}")
                st.caption(f"Peers: {data['peers']}")
                
                # Barra de Progresso simulando Sincronização
                st.write("Sync Progress:")
                st.progress(100 if node_name != "SP" else 85) 

    # 3. Gráfico de Tráfego de Rede Global
    st.write("---")
    st.subheader("📈 Network Traffic (Global)")
    traffic_data = data_bridge.get_network_history() 
    st.line_chart(traffic_data.set_index('Dia'))
    st.line_chart(traffic_data.set_index('Dia'))