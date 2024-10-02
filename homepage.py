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

# Container para a mensagem de boas-vindas
with st.container():

    st.markdown("<h1 style='text-align: center;'>Interface de consultas do CRM do CITi</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 20px;'>Navegue pelas opções no menu lateral para visualizar as análises e ferramentas disponíveis.</p>", unsafe_allow_html=True)

# Espaçamento
st.markdown("<br><br>", unsafe_allow_html=True)

# Container para FAQ
with st.container():
    st.markdown("<h2 style='text-align: center;'>Orientações Gerais 🔎 </h2>", unsafe_allow_html=True)
    
    # Organizar perguntas em colunas para uma visualização mais agradável
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("Qual a motivação da criação do site?"):
            st.write("""
            O site foi criado para centralizar e facilitar o acesso aos dados do CRM do CITi,
            proporcionando uma visualização intuitiva e prática.
            """)
        
        with st.expander("Como os dados foram obtidos?"):
            st.write("""
            Os dados foram extraídos diretamente do CRM, alimentado pelas equipes de Comercial.
            Através de um processo de ETL etc*
            """)

    with col2:
        with st.expander("Como utilizar o chat da plataforma?"):
            st.write("""
            O chat está disponível na aba 'Tire suas dúvidas com o chat', onde você poderá conhecer nosso CITiAssistant e tirar dúvidas sobre diversas informações do CRM de vendas.
            Use com moderação 🙂
            """)
        
        with st.expander("Quem pode acessar esses dados?"):
            st.write("""
            Qualquer pessoa do CITi pode ter acesso à plataforma, porém apenas membros autorizados da equipe do CITi  podem manipular os dados.
            
                     Pedimos que não compartilhem essas informações.
            """)
