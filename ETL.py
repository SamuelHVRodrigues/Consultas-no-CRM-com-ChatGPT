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
    mytoken = os.getenv('PIPEFY_TOKEN')
    PipeID = os.getenv('PIPE_ID')
    PipeReportID = os.getenv('PIPE_REPORT_ID')

    url = "https://api.pipefy.com/graphql"
    headers = {
        'Authorization': mytoken,
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

def get_data_gsheet():
    credentials_str = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    credentials = json.loads(credentials_str)
    
    # Acessa as variáveis de ambiente
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
    client = gspread.authorize(creds)
    SheetsID = os.getenv('SHEETS_ID')
    # Abre a planilha
    sheet = client.open_by_key(SheetsID)
    worksheet = sheet.worksheet('Base23')

    # Lê os dados
    data = worksheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
    return df
    
# a partir daqui, todas as variaveis que estão sendo usadas são do tipo DataFrame
def rename_columns_ENG(relatorio):
    relatorio.rename(columns={
        'Title': 'Nome do cliente',
        'Created at': 'Criado em',
        'Current phase': 'Fase atual',
        'Serviço': 'Checklist vertical',
        'Total time in Base de prospects (days)': 'Tempo total na fase Base de prospects (dias)',
        'Total time in Qualificação (days)': 'Tempo total na fase Qualificação (dias)',
        'Total time in Diagnóstico (days)': 'Tempo total na fase Diagnóstico (dias)',
        'Total time in Montagem de proposta (days)': 'Tempo total na fase Montagem de proposta (dias)',
        'Total time in Apresentação de proposta (days)': 'Tempo total na fase Apresentação de proposta (dias)',
        'Total time in Negociação (days)': 'Tempo total na fase Negociação (dias)',
        'First time enter Ganho': 'Primeira vez que entrou na fase Ganho',
        'Total time in Renegociação (days)': 'Tempo total na fase Renegociação (dias)',
    }, inplace=True)
        
def rename_columns_PTBR(relatorio):
    relatorio.rename(columns={
    'Título': 'Nome do cliente',
    'Serviço': 'Checklist vertical',
    }, inplace=True)

def reorganize_columns(relatorio):
    # Reorganiza as colunas
    # Alterando o nome das colunas com base nas colunas de Origem, e o idioma do relatório
    if 'Title' in relatorio.columns:
        rename_columns_ENG(relatorio)
    elif 'Título' in relatorio.columns:
        rename_columns_PTBR(relatorio)
    else:
        print("Colunas não encontradas.")
        return relatorio
    # Reordenando as colunas com base na ordem de origem
    colunas_ordenadas = [
        'Fase atual',
        'Criado em',
        'Nome do cliente',
        'Empresa',
        'Responsável',
        'Perfil de cliente',
        'Setor',
        'Checklist vertical',
        'Origem',
        'Valor Final',
        'Motivo da perda',
        'Motivo da não qualificação',
        'Tempo total na fase Base de prospects (dias)',
        'Tempo total na fase Qualificação (dias)',
        'Tempo total na fase Diagnóstico (dias)',
        'Tempo total na fase Montagem de proposta (dias)',
        'Tempo total na fase Apresentação de proposta (dias)',
        'Tempo total na fase Negociação (dias)',
        'Primeira vez que entrou na fase Ganho',
        'Tempo total na fase Renegociação (dias)'
    ]

    relatorio = relatorio[colunas_ordenadas]
    return relatorio


def type_fix(relatorio):
    # Convertendo colunas para os tipos corretos
    relatorio['Criado em'] = relatorio['Criado em'].astype(object)
    relatorio['Primeira vez que entrou na fase Ganho'] = relatorio['Primeira vez que entrou na fase Ganho'].astype(object)
    relatorio['Tempo total na fase Base de prospects (dias)'] = relatorio['Tempo total na fase Base de prospects (dias)'].astype(object)
    relatorio['Tempo total na fase Qualificação (dias)'] = relatorio['Tempo total na fase Qualificação (dias)'].astype(object)
    relatorio['Tempo total na fase Diagnóstico (dias)'] = relatorio['Tempo total na fase Diagnóstico (dias)'].astype(object)
    relatorio['Tempo total na fase Montagem de proposta (dias)'] = relatorio['Tempo total na fase Montagem de proposta (dias)'].astype(object)
    relatorio['Tempo total na fase Apresentação de proposta (dias)'] = relatorio['Tempo total na fase Apresentação de proposta (dias)'].astype(object)
    relatorio['Primeira vez que entrou na fase Ganho'] = relatorio['Primeira vez que entrou na fase Ganho'].astype(object)
    relatorio['Tempo total na fase Negociação (dias)'] = relatorio['Tempo total na fase Negociação (dias)'].astype(object)
    return relatorio

def treat_data(relatorio):
    # Trata os dados
    base23 = get_data_gsheet()
    relatorio = reorganize_columns(relatorio)
    relatorio = type_fix(relatorio)
    base_completa = pd.concat([relatorio, base23])
    # Converter 'Criado em' para datetime e Ordenar por data
    base_completa['Criado em'] = pd.to_datetime(base_completa['Criado em'], errors='coerce', dayfirst=True)
    base_completa = base_completa.sort_values(by='Criado em')

    # Preenchendo valores NaN com strings vazias
    atualizada = base_completa.fillna('')
    return atualizada

def UploadDataToGSheet(df):
    try:
        # Verifica se o DataFrame não está vazio
        if df.empty:
            print("O DataFrame está vazio. Nenhum dado será carregado para o Google Sheets.")
            return

        # Converte objetos Timestamp para string
        df = df.applymap(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, pd.Timestamp) else x)

        credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        credentials_dict = json.loads(credentials_json)

        # Acessa as variáveis de ambiente
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(creds)
        
        SheetsID = os.getenv('SHEETS_ID')
        if not SheetsID:
            print("SheetsID não foi encontrado nas variáveis de ambiente.")
            return

        # Abre a planilha
        sheet = client.open_by_key(SheetsID)
        worksheet = sheet.worksheet('Upload')

        # Limpa a planilha
        worksheet.clear()

        # Atualiza a planilha com os dados obtidos
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        print("Dados carregados com sucesso para o Google Sheets.")

        #obs. A planilha que está sendo atualizada é a que está alimentando o POWER BI

    # Tratamento de exceções    
    except FileNotFoundError:
        print("O arquivo 'credentials.json' não foi encontrado.")
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"A planilha com o ID {SheetsID} não foi encontrada.")
    except Exception as e:
        print(f"Ocorreu um erro durante o upload dos dados: {e}")



def ETLPipefy():
    # Chama a função para obter o relatório
    relatorio = get_data()
    print(relatorio) # Print para debug
    # Verifica se o relatório foi carregado corretamente e salva como Excel
    if relatorio is not None:
        #relatorio.to_excel('teste.xlsx', index=False) <--- Comentei para não salvar o arquivo
        print("Relatório salvo com sucesso.")
    else:
        print("Não foi possível extrair o relatório.")
    # Trata os dados
    relatorio = treat_data(relatorio)
    # Verifica se o relatório foi carregado corretamente e salva como Excel
    if relatorio is not None:
        #relatorio.to_excel('base_completa.xlsx', index=False) <--- Comentei para não salvar o arquivo
        print("Relatório salvo com sucesso.")
    else:
        print("Não foi possível extrair o relatório.")
    #upa as base atualizada para o Google Sheets
    UploadDataToGSheet(relatorio)


