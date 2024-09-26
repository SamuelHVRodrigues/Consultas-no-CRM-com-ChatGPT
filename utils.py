import pandas as pd
import streamlit as st
import altair as alt

@st.cache_data
def carregar_base():
    """
    Carrega a base de dados a partir de um arquivo CSV e realiza pré-processamentos iniciais.

    Returns:
        DataFrame: DataFrame contendo os dados carregados e pré-processados.
    """
    base = pd.read_csv("data/df_CRM.csv")
    base['Valor Final'] = pd.to_numeric(base['Valor Final'], errors='coerce')
    base['Data de cadastro'] = pd.to_datetime(base['Data de cadastro'], errors='coerce')
    base['Ano'] = base['Data de cadastro'].dt.year
    base = base.dropna(subset=['Valor Final', 'Data de cadastro'])
    return base

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
