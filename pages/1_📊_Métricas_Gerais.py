import streamlit as st
import altair as alt
from utils import (
    carregar_base,
    calcular_taxa_conversao,
    preparar_dados_faturamento,
    preparar_dados_analise_vendas,
)

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

# Filtro de ano
anos_disponiveis = sorted(base_ganho['Ano'].dropna().unique(), reverse=True)
anos_disponiveis.append('Tudo')
ano_selecionado = st.sidebar.selectbox("Selecione o ano:", anos_disponiveis)

# Filtrar base de acordo com o ano selecionado
if ano_selecionado != 'Tudo':
    base_filtrada = base_ganho[base_ganho['Ano'] == int(ano_selecionado)]
else:
    base_filtrada = base_ganho

# Cálculo de Faturamento e Total de Vendas
faturamento_total = base_filtrada['Valor Final'].sum()
total_vendas_ganhas = len(base_filtrada)

# Cálculo da Taxa de Conversão
if ano_selecionado != 'Tudo':
    base_ano = base[base['Ano'] == int(ano_selecionado)]
else:
    base_ano = base
taxa_conversao = calcular_taxa_conversao(base_ano)

# Criar colunas para o título e as métricas
col_title, col1, col2, col3 = st.columns([2, 1, 1, 1])

with col_title:
    st.markdown("# Métricas Gerais")
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
with col3:
    st.markdown(f"""
        <div class="metric">
            <div class="label">Taxa de Conversão</div>
            <div class="value">{taxa_conversao:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

# Espaçamento entre as métricas e os gráficos
st.markdown('<hr>', unsafe_allow_html=True)

# Preparar dados para o gráfico de faturamento
dados_faturamento = preparar_dados_faturamento(base_filtrada)

# Colunas de texto
col4, col5 = st.columns(2)

with col4:
    expander = st.expander("Resumo do ICP")
    expander.write("""
        O Perfil Ideal de Cliente (ICP) da empresa se concentra em empresas consolidadas do setor de Tecnologia da Informação (TI), que geralmente são provenientes da Comunidade CITi e buscam serviços relacionados ao Desenvolvimento Web com destaque para concepção. Essas empresas demonstram características como:
        
        - Taxas de sucesso elevadas e um alto volume de negócios fechados.
        - Menores tempos médios de fechamento de contratos, indicando um processo de venda mais eficiente.
        - Maiores retornos financeiros, o que evidencia um perfil mais rentável e estratégico para a empresa.
    """)


with col5:
    expander = st.expander("Funil de Vendas")
    expander.write("""
        Informações a respeito da situação atual do funil de vendas do CITi. (pensar se o formato será esse mesmo)
        
        - [Número atual de leads no funil]
        - [(Número de leads) : (Estágio do funil que está)]
        - [Demais informações sobre funil]
    """)

# Exibição dos gráficos lado a lado com Altair
col6, col7 = st.columns(2)

with col6:
    st.subheader(f"Faturamento Acumulado ({ano_selecionado})")
    # Resetar o índice para uso com Altair
    dados_faturamento = dados_faturamento.reset_index(drop=True)
    chart_faturamento = alt.Chart(dados_faturamento).mark_line(point=True).encode(
        x=alt.X('Data de cadastro:T', title='Data'),
        y=alt.Y('Faturamento Acumulado:Q', title='Faturamento Acumulado (R$)'),
        tooltip=[
            alt.Tooltip('Data de cadastro:T', title='Data'),
            alt.Tooltip('Faturamento Acumulado:Q', title='Faturamento (R$)')
        ]
    ).properties(
        height=350
    ).interactive()
    st.altair_chart(chart_faturamento, use_container_width=True)

with col7:
    # Criar uma linha com o subtítulo e os filtros alinhados horizontalmente
    subcol1, subcol2, subcol3 = st.columns([2, 1, 1])

    with subcol1:
        st.subheader("Análise de Vendas")
    with subcol2:
        st.selectbox("Métrica", ['Quantidade', 'Faturamento'], key='metrica')
    with subcol3:
        st.selectbox("Categoria", ['Origem', 'Setor', 'Perfil de cliente', 'Serviço'], key='categoria')

    # Recuperar os valores selecionados
    metrica = st.session_state['metrica']
    categoria = st.session_state['categoria']

    # Preparar dados para o gráfico de análise de vendas
    dados_analise_vendas = preparar_dados_analise_vendas(base_filtrada, metrica, categoria)

    # Exibir o gráfico
    dados_analise_vendas = dados_analise_vendas.reset_index(drop=True)
    if metrica == 'Quantidade':
        y_axis = alt.Y('Quantidade:Q', title='Quantidade')
    else:
        y_axis = alt.Y('Faturamento:Q', title='Faturamento (R$)')

    # Ajuste do eixo X para rótulos horizontais e evitar sobreposição
    x_axis = alt.X(
        f'{categoria}:N',
        sort='-x',
        title=categoria,
        axis=alt.Axis(
            labelAngle=0,
            labelOverlap='greedy',
            labelExpr="length(datum.label) > 15 ? substring(datum.label, 0, 15) + '\\n' + substring(datum.label, 15) : datum.label"
        )
    )

    chart_analise = alt.Chart(dados_analise_vendas).mark_bar().encode(
        x=x_axis,
        y=y_axis,
        tooltip=[alt.Tooltip(f'{categoria}:N', title=categoria), y_axis]
    ).properties(
        height=350
    ).interactive()
    st.altair_chart(chart_analise, use_container_width=True)
