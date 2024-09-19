import streamlit as st
import requests

st.title("Aplicação com OpenAI no Backend")

question = st.text_input("Digite sua pergunta:")

if st.button("Perguntar"):
    if question:
        response = requests.post("http://localhost:5000/ask", json={"question": question})
        if response.status_code == 200:
            data = response.json()
            st.subheader("Resposta:")
            st.write(data.get('answer'))
        else:
          st.write("Status code:", response.status_code)
          st.write("Resposta bruta:", response.text)  # Exibir a resposta bruta
          try:
              st.write("Resposta JSON:", response.json())  # Tente fazer o parsing do JSON
          except ValueError as e:
              st.write("Erro ao fazer o parsing do JSON:", e)