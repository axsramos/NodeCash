import streamlit as st
from styles import apply_styles
from views import overview, node_detail, financials

# Configuração e Estilo
st.set_page_config(page_title="NodeCash Dashboard", layout="wide")
apply_styles()  # Aplica o nosso Design System

def main():
    st.sidebar.image("https://placekitten.com/100/100") # Placeholder para logo
    st.sidebar.title("NodeCash 💎")
    
    page = st.sidebar.radio("Navegação:", ["Health Global", "Node BR", "Financeiro"])

    if page == "Health Global":
        overview.render()
    elif page == "Node BR":
        node_detail.render("BR")
    elif page == "Financeiro":
        financials.render()

if __name__ == "__main__":
    main()