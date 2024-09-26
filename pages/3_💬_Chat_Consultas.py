import streamlit as st
import requests
import pandas as pd
import tiktoken  # Biblioteca para calcular tokens

# Função para contar tokens de entrada
def contar_tokens(texto):
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")  # Altere para o modelo gpt-4o-mini
    return len(encoding.encode(texto))

# Definir limites de tokens
MAX_TOKENS_INPUT = 100  # Exemplo: limite de 100 tokens de entrada

# Carregar a base de dados que foi tratada em outro arquivo
df = pd.read_csv(r'data/df_CRM.csv')

# Inicializar o estado da sessão para armazenar o histórico
if 'historico' not in st.session_state:
    st.session_state.historico = []

# Título da aplicação
st.title("Interface para Perguntas sobre a Base de Dados")

# Adiciona a tabela da base de dados
st.subheader("Tabela Completa")
st.dataframe(df)

# Entrada de pergunta
question = st.text_input("Digite sua pergunta:")

# Contar tokens da pergunta
tokens_usados = contar_tokens(question)
st.write(f"Tokens usados na pergunta: {tokens_usados}/{MAX_TOKENS_INPUT}")

# Lidar com o botão de enviar pergunta
if st.button("Perguntar"):
    if tokens_usados > MAX_TOKENS_INPUT:
        st.warning(f"A pergunta excede o limite máximo de {MAX_TOKENS_INPUT} tokens.")
    elif question:
        # Fazer a requisição para a API do back-end
        response = requests.post("http://15.228.13.32:3333/ask", json={"question": question})
        if response.status_code == 200:
            data = response.json()
            resposta = data.get('answer')
            tokens_saida = data.get('tokens_usados', 'Não disponível')  # Pega o número de tokens usados na resposta

            # Mostrar a resposta e os tokens usados
            st.subheader("Resposta:")
            st.write(resposta)
            st.write(f"Tokens usados na resposta: {tokens_saida}")

            # Adicionar ao histórico
            st.session_state.historico.append({"pergunta": question, "resposta": resposta, "tokens": tokens_saida})
        else:
            st.write("Status code:", response.status_code)
            st.write("Resposta bruta:", response.text)
            try:
                st.write("Resposta JSON:", response.json())
            except ValueError as e:
                st.write("Erro ao fazer o parsing do JSON:", e)

# Exibir histórico de perguntas e respostas em um expander (minimizável)
with st.expander("Histórico de Perguntas e Respostas", expanded=False):
    if st.session_state.historico:
        for entry in st.session_state.historico:
            st.write(f"**Pergunta**: {entry['pergunta']}")
            st.write(f"**Resposta**: {entry['resposta']}")
            st.write(f"**Tokens usados**: {entry['tokens']}")
            st.write("----------------------------------------------------")



