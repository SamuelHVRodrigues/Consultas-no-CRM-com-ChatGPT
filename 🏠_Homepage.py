import streamlit as st

# Configurações globais da página
st.set_page_config(
    page_title="CRM de Vendas",
    page_icon="assets/Logo.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Colunas para melhorar a disposição da pagina
col1, col2 = st.columns([0.5,2])

with col1:
    # Exibição da imagem do logo
    st.image("assets/icon_citi.png")
with col2:
    st.markdown("<h1 style='text-align: start; text-indent: 25px;'>Interface de consultas do CRM do CITi</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='width: 71%; height: 2px; margin-top: 0px; margin-bottom: 25px;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: start; font-size: 20px; font-weight: 520; margin-bottom: 45px;'>Navegue pelas opções no menu lateral para visualizar as análises e ferramentas disponíveis.</p>", unsafe_allow_html=True)


# Container para FAQ
with st.container():
    st.markdown("<h2 style='text-align: center;'>Informações Gerais 🔎 </h2>", unsafe_allow_html=True)
    
    # Organizar perguntas em colunas para uma visualização mais agradável
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("Qual a motivação da criação do site?"):
            st.write("""
            A interface foi criada com a finalidade de ser uma ferramenta para centralizar e facilitar o acesso aos dados do CRM de vendas,
            proporcionando uma visualização intuitiva e prática pela equipe de Comercial e Diretoria.
            Por isso, o objetivo principal é auxiliar na tomada de decisões estratégicas e na compreensão do cenário do CRM.
            """)
        
        with st.expander("Como os dados foram obtidos?"):
            st.markdown("""
            Os dados foram extraídos a partir do CRM de Vendas presente no Pipefy e alimentado pela equipe de Comercial. <br>
            Usando a API da plataforma e integrando com o Google Sheets, conseguimos ter uma base de dados que atualiza automaticamente e fornece o conteúdo para essa interface 🤯.
            """, unsafe_allow_html=True)

    with col2:
        with st.expander("Como utilizar o chat da plataforma?"):
            st.write("""
            O chat está disponível na aba 'Chat Consultas', onde você poderá conhecer nosso CITiAssistant e tirar dúvidas sobre diversas informações do CRM de vendas.
            Use com moderação 💚.
            """)
        
        with st.expander("Quem pode acessar esses dados?"):
            st.write("""
            A Interface de Consultas do CRM foi desenvolvida exclusivamente para uso pelo time de Negócios e pela Direx.
                     
                     Pedimos que não compartilhem essas informações.
            """)
