import streamlit as st
import requests
from dotenv import load_dotenv, find_dotenv, dotenv_values

# Carregar variáveis de ambiente
_ = load_dotenv(find_dotenv())
env_vars = dotenv_values(find_dotenv())
server_url = env_vars.get('SERVER_URL')

st.title("Aplicação com OpenAI no Backend")

question = st.text_input("Digite sua pergunta:")

if st.button("Perguntar"):
    if question:
        response = requests.post(server_url, json={"question": question})
        if response.status_code == 200:
            data = response.json()
            st.subheader("Resposta:")
            st.write(data.get('answer'))
        else:
          st.write("Status code:", response.status_code)
          st.write("Resposta bruta:", response.text)
          try:
              st.write("Resposta JSON:", response.json())
          except ValueError as e:
              st.write("Erro ao fazer o parsing do JSON:", e)
