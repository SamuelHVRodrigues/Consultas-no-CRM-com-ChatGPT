import pandas as pd
import streamlit as st
import altair as alt

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe, get_as_dataframe

def carregar_base():
    credentials = st.secrets["google_service_account"]

    # Acessa as variáveis de ambiente
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope) # Verificar 'os.path.join(os.getcwd()' para puxar as credenciais
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

    df['Valor Final'] = pd.to_numeric(df['Valor Final'], errors='coerce')
    df['Criado em'] = pd.to_datetime(df['Criado em'], errors='coerce')
    df['Primeira vez que entrou na fase Ganho'] = pd.to_datetime(df['Primeira vez que entrou na fase Ganho'], errors='coerce')
    df['Ano'] = df['Criado em'].dt.year
    df.rename(columns={'Responsável': 'Vendedor'}, inplace=True)
    df.rename(columns={'Checklist vertical': 'Serviço'}, inplace=True)
    # Remover colunas sem nome ou colunas com nomes vazios
    df = df.loc[:, ~df.columns.str.match('^Unnamed')]
    df = df.loc[:, df.columns != '']
    
    colunas_tempo = definir_colunas_tempo()
    
    # Converter as colunas de tempo para float
    df[colunas_tempo] = df[colunas_tempo].apply(pd.to_numeric, errors='coerce')
    return df

# Lista das colunas de tempo
def definir_colunas_tempo():
    colunas_tempo = [
        'Tempo total na fase Base de prospects (dias)',
        'Tempo total na fase Qualificação (dias)',
        'Tempo total na fase Diagnóstico (dias)',
        'Tempo total na fase Montagem de proposta (dias)',
        'Tempo total na fase Apresentação de proposta (dias)',
        'Tempo total na fase Negociação (dias)',
        'Tempo total na fase Renegociação (dias)'
    ]
    
    return colunas_tempo

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
        DataFrame: DataFrame com 'Criado em' e 'Faturamento Acumulado'.
    """
    base_faturamento = base_filtrada.groupby('Criado em')['Valor Final'].sum().reset_index()
    base_faturamento = base_faturamento.sort_values('Criado em')
    base_faturamento['Faturamento Acumulado'] = base_faturamento['Valor Final'].cumsum()
    return base_faturamento[['Criado em', 'Faturamento Acumulado']]

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
    # Usamos uma cópia do DataFrame original para evitar alterações indesejadas
    df = base_filtrada.copy()

    # Aplicamos a lógica de dividir e explodir apenas se a categoria for 'Serviço'
    # e se estivermos calculando a 'Quantidade', para não afetar o 'Faturamento' ou outros cálculos
    if categoria == 'Serviço' and metrica == 'Quantidade':
        # Dividir os serviços separados por vírgula em listas
        df['Serviço'] = df['Serviço'].str.split(', ')
        # Explodir a coluna 'Serviço' para que cada serviço tenha sua própria linha
        df = df.explode('Serviço')

    # Agrupamos e agregamos os dados de acordo com a métrica selecionada
    if metrica == 'Quantidade':
        base_agrupado = df.groupby(categoria).size().reset_index(name='Quantidade')
    else:
        base_agrupado = df.groupby(categoria)['Valor Final'].sum().reset_index()
        base_agrupado.rename(columns={'Valor Final': 'Faturamento'}, inplace=True)

    return base_agrupado


def preparar_dados_metricas_vendedores(base_filtrada, metrica):
    """
    Prepara os dados para o gráfico de metricas de vendedores.

    Args:
        base_filtrada (DataFrame): DataFrame com os dados filtrados.

    Returns:
        DataFrame: DataFrame com 'Vendedor' e 'Faturamento'.
    """
    if metrica == 'Quantidade':
        base_metricas = base_filtrada.groupby('Vendedor').size().reset_index(name='Quantidade')
    else:
        base_metricas = base_filtrada.groupby('Vendedor')['Valor Final'].sum().reset_index()
        base_metricas.rename(columns={'Valor Final': 'Faturamento'}, inplace=True)
        base_metricas = base_metricas.sort_values('Faturamento', ascending=False)
    return base_metricas
