import streamlit as st

# Configurações globais da página
st.set_page_config(
    page_title="CRM de Vendas",
    page_icon="assets/Logo.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização com CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Exibição da imagem do logo
st.image("assets/icon_citi.png")

st.title("Bem-Vinde à Interface de Consultas do CRM do CITi")

# Mensagem ou conteúdo adicional na tela inicial
st.write("Navegue pelas opções no menu lateral para visualizar as métricas e análises disponíveis.")