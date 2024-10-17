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
    base = pd.read_csv("data/base_mockada.csv")
    base['Valor Final'] = pd.to_numeric(base['Valor Final'], errors='coerce')
    base['Data de cadastro'] = pd.to_datetime(base['Data de cadastro'], errors='coerce')
    base['Ano'] = base['Data de cadastro'].dt.year
    base = base.dropna(subset=['Valor Final', 'Data de cadastro'])
    base.rename(columns={'Checklist vertical': 'Serviço'}, inplace=True)

    # Lista das colunas de tempo
    colunas_tempo = [
        'Tempo total na fase Base de prospects (dias)',
        'Tempo total na fase Qualificação (dias)',
        'Tempo total na fase Diagnóstico (dias)',
        'Tempo total na fase Montagem de proposta (dias)',
        'Tempo total na fase Apresentação de proposta (dias)',
        'Tempo total na fase Negociação (dias)',
        'Tempo total na fase Renegociação (dias)'
    ]

    # Converter as colunas de tempo para float
    base[colunas_tempo] = base[colunas_tempo].apply(pd.to_numeric, errors='coerce')

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
    # Usamos uma cópia do DataFrame original para evitar alterações indesejadas
    df_analise_vendas = base_filtrada.copy()

    # Aplicamos a lógica de dividir e explodir apenas se a categoria for 'Serviço'
    # e se estivermos calculando a 'Quantidade', para não afetar o 'Faturamento' ou outros cálculos
    if categoria == 'Serviço' and metrica == 'Quantidade':
        # Dividir os serviços separados por vírgula em listas
        df_analise_vendas['Serviço'] = df_analise_vendas['Serviço'].str.split(', ')
        # Explodir a coluna 'Serviço' para que cada serviço tenha sua própria linha
        df_analise_vendas = df_analise_vendas.explode('Serviço')

    # Agrupamos e agregamos os dados de acordo com a métrica selecionada
    if metrica == 'Quantidade':
        base_agrupado = df_analise_vendas.groupby(categoria).size().reset_index(name='Quantidade')
    else:
        base_agrupado = df_analise_vendas.groupby(categoria)['Valor Final'].sum().reset_index()
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