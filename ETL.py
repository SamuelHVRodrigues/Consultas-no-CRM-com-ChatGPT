import pandas as pd
import numpy as np
import requests
import json
from io import BytesIO
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

def get_data():
    # Acessa as variáveis de ambiente
    mytoken = os.getenv('mytoken')
    PipeID = os.getenv('PipeID')
    PipeReportID = os.getenv('PipeReportID')

    url = "https://api.pipefy.com/graphql"
    headers = {
        'Authorization': 'Bearer ' + mytoken,
        'Content-Type': 'application/json'
    }

    mutation = f"""
    mutation {{
        exportPipeReport(input: {{pipeId: {PipeID}, pipeReportId: {PipeReportID}}}) {{
            pipeReportExport {{
                id
            }}
        }}
    }}
    """

    response = requests.post(url, json={'query': mutation}, headers=headers)
    
    # Verifica se a requisição foi bem-sucedida
    if response.status_code != 200:
        print(f"Erro na requisição: Status {response.status_code}")
        print("Resposta:", response.text)
        return None

    response_json = response.json()
    # Verifica se a chave 'data' existe
    if 'data' not in response_json:
        print("Resposta inesperada da API:", response_json)
        return None

    export_id = response_json['data']['exportPipeReport']['pipeReportExport']['id']
    
    # Query GraphQL
    query = f"""
    {{
        pipeReportExport(id: "{export_id}") {{
            fileURL
            state
            startedAt
            requestedBy {{
                id
            }}
        }}
    }}
    """

    download_response = requests.post(url, json={'query': query}, headers=headers)

    # Verifica se a segunda requisição foi bem-sucedida
    if download_response.status_code != 200:
        print(f"Erro na segunda requisição: Status {download_response.status_code}")
        print("Resposta:", download_response.text)
        return None

    download_response_json = download_response.json()
    # Verifica se 'data' e 'pipeReportExport' existem na resposta
    if 'data' not in download_response_json or 'pipeReportExport' not in download_response_json['data']:
        print("Resposta inesperada da API na segunda requisição:", download_response_json)
        return None

    file_url = download_response_json['data']['pipeReportExport']['fileURL']
    r = requests.get(file_url, allow_redirects=True)
    data = r.content
    try:
        relatorio = pd.read_excel(BytesIO(data), engine='openpyxl')  # Lê o arquivo Excel
        return relatorio
    except Exception as e:
        print("Erro na extração:", e)
        return None

# Chama a função para obter o relatório
relatorio = get_data()
print(type(relatorio))
# Verifica se o relatório foi carregado corretamente e salva como Excel
if relatorio is not None:
    relatorio.to_excel('teste.xlsx', index=False)
    print("Relatório salvo com sucesso como 'teste.xlsx'.")
else:
    print("Não foi possível extrair o relatório.")
