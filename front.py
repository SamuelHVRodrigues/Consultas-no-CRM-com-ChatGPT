import streamlit as st
import requests

st.title("Aplicação com OpenAI no Backend")

question = st.text_input("Digite sua pergunta:")

if st.button("Perguntar"):
    if question:
        response = requests.post("http://15.228.13.32:3333/ask", json={"question": question})
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
