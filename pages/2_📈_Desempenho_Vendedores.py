import streamlit as st
import pandas as pd
import plotly.express as px
from utils import carregar_base, calcular_taxa_conversao

# Título da página
st.title("Análise de Desempenho Individual")

# Carregar a base de dados
base = carregar_base()

# Selecionar vendedor
vendedores = base['Vendedor'].dropna().unique()  # Alterado para 'Vendedor' na nova base
vendedor_selecionado = st.sidebar.selectbox("Selecione o Vendedor:", vendedores)

# Filtro de ano
anos_disponiveis = sorted(base['Ano'].dropna().unique(), reverse=True)
anos_disponiveis.append('Tudo')
ano_selecionado = st.sidebar.selectbox("Selecione o ano:", anos_disponiveis)

# Filtrar base de acordo com o vendedor e ano selecionados
base_vendedor = base[base['Vendedor'] == vendedor_selecionado]

if ano_selecionado != 'Tudo':
    base_vendedor = base_vendedor[base_vendedor['Ano'] == int(ano_selecionado)]

# Filtrar vendas ganhas
base_ganho = base_vendedor[base_vendedor['Fase atual'] == 'Ganho']

# Cálculo de Faturamento e Taxa de Conversão
faturamento_total = base_ganho['Valor Final'].sum()
taxa_conversao = calcular_taxa_conversao(base_vendedor)

# Exibir métricas
col1, col2, col3 = st.columns(3)
col1.metric("Faturamento", f"R$ {faturamento_total:,.2f}")
col2.metric("Total de Vendas", len(base_ganho))
col3.metric("Taxa de Conversão", f"{taxa_conversao:.2f}%")

# Gráfico de Vendas por Mês
if not base_ganho.empty:
    base_ganho['Mês'] = pd.to_datetime(base_ganho['Data de cadastro']).dt.strftime('%Y-%m')  # Atualizado para 'Data de cadastro'
    vendas_por_mes = base_ganho.groupby('Mês')['Valor Final'].sum().reset_index()

    st.subheader("Faturamento por Mês")
    fig = px.bar(
        vendas_por_mes,
        x='Mês',
        y='Valor Final',
        title=f'Faturamento Mensal - {vendedor_selecionado} ({ano_selecionado})',
        labels={'Valor Final': 'Faturamento (R$)', 'Mês': 'Mês'}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Não há dados de vendas ganhas para os filtros selecionados.")
