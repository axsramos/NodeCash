import streamlit as st
from utils import data_bridge

def render():
    st.title("💰 Financial Insights")
    st.markdown("Monitoramento de rendimentos e projeções de ROI.")

    # Busca os dados no Bridge
    fin_data = data_bridge.get_financial_summary()
    history_df = data_bridge.get_network_history() # Usaremos os dados simulados aqui

    # 1. Cards de Resumo (Top Row)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Acumulado", f"R$ {fin_data['total_brl']:.2f}", "+R$ 15,30")
    
    with col2:
        st.metric("Yield Diário (Médio)", f"R$ {fin_data['daily_yield']:.2f}", "Stable")
        
    with col3:
        # Cálculo simples de ROI estimado (LaTeX para formalizar a métrica)
        # $$ROI = \frac{Ganho - Custo}{Custo}$$
        st.metric("Estimativa Mensal", f"R$ {fin_data['estimated_monthly']:.2f}", "7.2%")

    st.write("---")

    # 2. Gráfico de Rendimento por Node (Bar Chart)
    st.subheader("📊 Rendimento por Node (Últimos 7 dias)")
    
    # Transformando os dados para um formato de "Cash" para o gráfico
    earnings_df = history_df.copy()
    # Simulando que cada unidade de tráfego gera R$ 0.50
    for col in ["Node BR", "Node SC", "Node SP"]:
        earnings_df[col] = earnings_df[col] * 0.50
        
    st.bar_chart(earnings_df.set_index('Dia'))

    # 3. Tabela de Transações Recentes
    st.subheader("📝 Extrato de Recompensas")
    st.dataframe(
        earnings_df.tail(5), 
        use_container_width=True,
        hide_index=True
    )