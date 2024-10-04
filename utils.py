import pandas as pd
import streamlit as st
import altair as alt

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe, get_as_dataframe
import os

def carregar_base():
    # Acessa as variáveis de ambiente
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(os.getcwd(), 'credentials.json'), scope) # Verificar 'os.path.join(os.getcwd()' para puxar as credenciais
    client = gspread.authorize(creds)
    
    # Insira o ID da planilha diretamente para testar
    SheetsID = '18Ub6-90lW3CXIpezs2Sjrtx5tlnRhMBaUEY_Jz30hHg' # Verificar para substituir o código bruto
    
    # Abre a planilha
    sheet = client.open_by_key(SheetsID)
    worksheet = sheet.worksheet('Upload')

    # Lê os dados
    data = worksheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
    return df


def calcular_taxa_conversao(base):
    """
    Calcula a taxa de conversão com base nos dados fornecidos.

    Args:
        base (DataFrame): DataFrame com os dados filtrados.

    Returns:
        float: Taxa de conversão calculada.
    """
    total_vendas_ganhas = len(base[base['Fase atual'] == 'Ganho'])
    total_oportunidades = len(base)
    taxa_conversao = (total_vendas_ganhas / total_oportunidades) * 100 if total_oportunidades > 0 else 0
    return taxa_conversao

def preparar_dados_faturamento(base_filtrada):
    """
    Prepara os dados para o gráfico de faturamento acumulado.

    Args:
        base_filtrada (DataFrame): DataFrame com os dados filtrados.

    Returns:
        DataFrame: DataFrame com 'Data de cadastro' e 'Faturamento Acumulado'.
    """
    base_faturamento = base_filtrada.groupby('Data de cadastro')['Valor Final'].sum().reset_index()
    base_faturamento = base_faturamento.sort_values('Data de cadastro')
    base_faturamento['Faturamento Acumulado'] = base_faturamento['Valor Final'].cumsum()
    return base_faturamento[['Data de cadastro', 'Faturamento Acumulado']]

def preparar_dados_analise_vendas(base_filtrada, metrica, categoria):
    """
    Prepara os dados para o gráfico de análise de vendas.

    Args:
        base_filtrada (DataFrame): DataFrame com os dados filtrados.
        metrica (str): Métrica selecionada ('Quantidade' ou 'Faturamento').
        categoria (str): Categoria selecionada para agrupamento.

    Returns:
        DataFrame: DataFrame preparado para o gráfico.
    """
    if metrica == 'Quantidade':
        base_agrupado = base_filtrada.groupby(categoria).size().reset_index(name='Quantidade')
    else:
        base_agrupado = base_filtrada.groupby(categoria)['Valor Final'].sum().reset_index()
        base_agrupado.rename(columns={'Valor Final': 'Faturamento'}, inplace=True)
    return base_agrupado
