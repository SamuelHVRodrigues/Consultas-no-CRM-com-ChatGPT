import streamlit as st
import requests
import pandas as pd
import tiktoken  # Biblioteca para calcular tokens
import shelve
from dotenv import load_dotenv
from utils import carregar_base

# Carrega as variáveis do arquivo .env
load_dotenv()

# Função para contar tokens de entrada
def contar_tokens(texto):
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")  # Altere para o modelo gpt-4o-mini
    return len(encoding.encode(texto))

# Estilização com CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Definir limites de tokens
MAX_TOKENS_INPUT = 100  # Exemplo: limite de 100 tokens de entrada

# Carregar a base de dados diretamente do sheets
df = carregar_base()

# Inicializar o estado da sessão para armazenar o histórico
if 'historico' not in st.session_state:
    st.session_state.historico = []

# Funções para salvar e carregar histórico de chat usando shelve
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

# Inicializa ou carrega o histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Adicionar título na página
st.title("CITiAssistant")  # Título principal da página

# Criar uma barra lateral para o histórico
st.sidebar.title("CITiAssistant")  # Adiciona o título na barra lateral
st.sidebar.header("Histórico do Chat Atual")

# Botão para limpar histórico de mensagens
if st.sidebar.button("Limpar Histórico"):
    st.session_state.messages.clear()  # Limpa o histórico de mensagens
    st.session_state.historico.clear()  # Limpa o histórico de perguntas e respostas
    save_chat_history(st.session_state.messages)  # Atualiza o histórico salvo
    st.sidebar.success("Histórico limpo com sucesso!")  # Mensagem de sucesso

USER_AVATAR = "🐷"
BOT_AVATAR = "🤖"

# Tabela dentro de um botão expansível
with st.expander("Visualizar Tabela Completa", expanded=False):
    st.dataframe(df)

route = st.secrets["ROUTE"]

# Interface de chat
if prompt := st.chat_input("Mensagem CITiAssistant:"):
    tokens_usados_pergunta = contar_tokens(prompt)
    
    if tokens_usados_pergunta > MAX_TOKENS_INPUT:
        st.warning(f"A pergunta excede o limite máximo de {MAX_TOKENS_INPUT} tokens.")
    else:
        # Fazer a requisição para a API
        response = requests.post(route, json={"question": prompt})
        if response.status_code == 200:
            data = response.json()
            resposta = data.get('answer')
            tokens_usados_resposta = data.get('tokens_usados', 'Não disponível')  # Pega o número de tokens usados na resposta

            # Adicionar a pergunta e resposta no histórico
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": resposta})

            # Adicionar ao histórico
            st.session_state.historico.append({"pergunta": prompt, "resposta": resposta, "tokens_pergunta": tokens_usados_pergunta, "tokens_resposta": tokens_usados_resposta})
        else:
            st.write(f"Erro: {response.status_code}")
            st.write(response.text)

# Exibir mensagens anteriores (em ordem cronológica)
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Sidebar com histórico de perguntas e respostas em formato expansível
with st.sidebar.expander("Histórico de Perguntas e Respostas", expanded=True):  # Expandido por padrão
    if st.session_state.historico:
        for entry in st.session_state.historico:
            st.write(f"**Pergunta**: {entry['pergunta']}")
            st.write(f"**Resposta**: {entry['resposta']}")
            st.write(f"**Tokens usados na pergunta**: {entry['tokens_pergunta']}")
            st.write(f"**Tokens usados na resposta**: {entry['tokens_resposta']}")
            st.write("----------------------------------------------------")
    else:
        st.write("Nenhum histórico disponível.")

# Salvar o histórico após cada interação
save_chat_history(st.session_state.messages)
