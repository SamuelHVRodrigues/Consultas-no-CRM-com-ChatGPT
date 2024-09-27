import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from utils import carregar_base, calcular_taxa_conversao

# Configurar a página para ter layout largo
st.set_page_config(layout="wide")

# Estilização adicional para ajustar alinhamentos e espaçamentos
st.markdown("""
    <style>
        /* Reduzir o espaçamento acima do título */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 1rem;
        }
        /* Centralizar texto dentro das colunas */
        .metric {
            text-align: center;
        }
        .metric .label {
            font-size: 1rem;
            color: grey;
        }
        .metric .value {
            font-size: 1.5rem;
            font-weight: bold;
        }
        /* Ajustar o espaçamento da linha horizontal */
        hr {
            margin-top: -10px; /* Ajuste para mover a linha mais para cima */
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
# Carregar a base de dados
base = carregar_base()

# Filtrar somente vendas ganhas
base_ganho = base[base['Fase atual'] == 'Ganho']

# Sidebar para seleção do ano
anos_disponiveis = sorted(base_ganho['Ano'].dropna().unique(), reverse=True)
ano_selecionado = st.sidebar.radio("Selecione o ano:", anos_disponiveis)

# Filtrar base pelo ano selecionado
base_ano = base_ganho[base_ganho['Ano'] == int(ano_selecionado)]

# Obter lista de vendedores no ano selecionado
vendedores_disponiveis = base_ano['Vendedor'].dropna().unique()
vendedores_disponiveis = sorted(vendedores_disponiveis)

# Sidebar para seleção do vendedor
vendedor_selecionado = st.sidebar.selectbox("Selecione o vendedor:", ['Todos'] + list(vendedores_disponiveis))
# Filtrar base de acordo com o ano selecionado
if ano_selecionado != 'Tudo':
    base_filtrada = base_ganho[base_ganho['Ano'] == int(ano_selecionado)]
else:
    base_filtrada = base_ganho


# Cálculo de Faturamento e Total de Vendas
faturamento_total = base_filtrada['Valor Final'].sum()
total_vendas_ganhas = len(base_filtrada)


# Criar colunas para o título e gráficos
col_title, col1, col2 = st.columns([2, 3, 3])

with col_title:
    st.markdown("## Desempenho Individual")
# Ao lado do col_title exibir o tempo médio de fechamento, quantidade de vendas e faturamento

with col2:
    st.markdown(f"""
        <div class="metric">
            <div class="label">Total de Vendas</div>
            <div class="value">{total_vendas_ganhas}</div>
        </div>
        """, unsafe_allow_html=True)

 #Espaçamento entre as métricas e os gráficos
st.markdown('<hr>', unsafe_allow_html=True)    

# Exibição dos gráficos gerais se o vendedor selecionado for 'Todos'
if vendedor_selecionado == 'Todos':
    with col1:
        st.markdown(f"""
                <div class="metric">
            <div class="label">Faturamento</div>
            <div class="value">R$ {faturamento_total:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric">
                <div class="label">Total de Vendas</div>
                <div class="value">{total_vendas_ganhas}</div>
            </div>
            """, unsafe_allow_html=True)

    # Gráfico 1: Faturamento por Vendedor
    faturamento_vendedor = base_ano.groupby('Vendedor')['Valor Final'].sum().reset_index()
    grafico_faturamento = alt.Chart(faturamento_vendedor).mark_bar().encode(
        x=alt.X('Vendedor:N', title='Vendedor', sort='-y'),
        y=alt.Y('Valor Final:Q', title='Faturamento'),
        tooltip=['Vendedor', 'Valor Final']
    ).properties(
        title="Faturamento por Vendedor",
        height=350
    ).interactive()
    
    # Gráfico 2: Funil de Vendas Total
        # 1° Filtrar negociações que ainda estão em aberto
    fases_excluidas = ["Ganho", "Perdido", "Não-qualificado"]
    base_aberto = base[(base['Ano'] == int(ano_selecionado)) & (~base['Fase atual'].isin(fases_excluidas))]
        # 2° Agrupar por fase atual e contar a quantidade de negociações abertas em cada fase
    grafico_total = base_aberto.groupby('Fase atual').size().reset_index(name='Quantidade')

        # 3° Criar o gráfico 
    grafico_funil = alt.Chart(grafico_total).mark_bar().encode(
    x=alt.X('Fase atual:N', title='Fase', sort='-y'),
    y=alt.Y('Fase atual:N', sort='-x', title="Fase"),
    tooltip=['Fase atual', 'Quantidade']
    ).properties(
    title="Funil de Vendas",
    height=350
    ).interactive()


    # Gráfico 3: Taxa de Conversão por Vendedor
    base_vendas = base[base['Ano'] == int(ano_selecionado)]
    taxa_conversao_vendedores = base_vendas.groupby('Vendedor').apply(calcular_taxa_conversao).reset_index()
    taxa_conversao_vendedores.columns = ['Vendedor', 'Taxa de Conversão']
    grafico_taxa_conversao = alt.Chart(taxa_conversao_vendedores).mark_bar().encode(
        y=alt.Y('Vendedor:N', title='Vendedor', sort='-x'),
        x=alt.X('Taxa de Conversão:Q', title='Taxa de Conversão (%)'),
            tooltip=['Vendedor', 'Taxa de Conversão']
        ).properties(
        title="Taxa de Conversão por Vendedor",
        height=350
        ).interactive()

# Layout dos gráficos: Taxa de conversão ao lado do faturamento, e funil de vendas abaixo
    col1, col2 = st.columns(2)

    with col1:
        st.altair_chart(grafico_taxa_conversao, use_container_width=True)

    with col2:
        st.altair_chart(grafico_faturamento, use_container_width=True)

    # Exibir o gráfico de funil abaixo
    st.altair_chart(grafico_funil, use_container_width=True)

# Se um vendedor for selecionado
else:
    # Filtrar a base de dados do vendedor selecionado
    base_vendedor = base_ano[base_ano['Vendedor'] == vendedor_selecionado]
    
    # Mostrar informações do vendedor
    st.markdown(f"### Desempenho de {vendedor_selecionado}")
    
    # Exibir as informações dos leads do vendedor
    st.dataframe(base_vendedor[['Nome do cliente', 'Setor', 'Valor Final', 'Data de cadastro', 'Origem', 'Checklist vertical', 'Perfil de cliente']])

    # Faturamento acumulado do vendedor
    with col1:
        faturamento_acumulado = base_vendedor['Valor Final'].sum()
        st.markdown(f"""
            <div class="metric">
                <div class="label">Faturamento Acumulado</div>
                <div class="value">{faturamento_acumulado}</div>
            </div>
            """, unsafe_allow_html=True)
        

    
   
