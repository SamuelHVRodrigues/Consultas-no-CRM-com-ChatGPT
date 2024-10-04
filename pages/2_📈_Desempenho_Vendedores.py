import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from utils import (
    carregar_base,
    calcular_taxa_conversao,
    preparar_dados_faturamento,
    preparar_dados_metricas_vendedores,
)

# Configurar a página para ter layout largo
st.set_page_config(layout="wide",
                   page_title="Desempenho Individual",
                   page_icon="assets/Logo.svg")

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



# Verificar se algum valor em 'Vendedor' tem múltiplos nomes e dividir
base['Vendedor'] = base['Vendedor'].str.split(', ')
base = base.explode('Vendedor')  # Separar os vendedores em linhas individuais

# **Manter apenas Nome e Sobrenome**
base['Vendedor'] = base['Vendedor'].apply(lambda x: ' '.join(x.split()[:2]))

# Sidebar para seleção do ano
anos_disponiveis = sorted(base_ganho['Ano'].dropna().unique(), reverse=True)
ano_selecionado = st.sidebar.radio("Selecione o ano:", anos_disponiveis)

# Filtrar a base geral pelo ano selecionado
base_filtrada = base[base['Ano'] == int(ano_selecionado)]
# Filtrar base ganha pelo ano selecionado
base_filtrada_ganho = base_ganho[base_ganho['Ano'] == int(ano_selecionado)]


# Atualizar lista de vendedores com base no ano selecionado
vendedores_disponiveis = sorted(base_filtrada['Vendedor'].dropna().unique())

# Adicionar a opção 'Todos' como primeira escolha
vendedores_disponiveis = ['Todos'] + vendedores_disponiveis
# Sidebar para seleção do vendedor
vendedor_selecionado = st.sidebar.selectbox("Selecione o vendedor:", list(vendedores_disponiveis))


# Filtrar a base e modificar o título de acordo com o vendedor selecionado
if vendedor_selecionado != 'Todos':
    base_filtrada = base_filtrada[base_filtrada['Vendedor'] == vendedor_selecionado]
    base_filtrada_ganho = base_filtrada_ganho[base_filtrada_ganho['Vendedor'] == vendedor_selecionado]

# Faturamento total, número de vendas ganhas e taxa de conversão
faturamento_total = base_filtrada_ganho['Valor Final'].sum()
total_vendas_ganhas = len(base_filtrada_ganho)
taxa_conversao = calcular_taxa_conversao(base_filtrada)

# Cálculo do tempo médio de fechamento 
tempo_medio_fechamento = base_filtrada_ganho[
    ['Tempo total na fase Base de prospects (dias)', 'Tempo total na fase Qualificação (dias)',
     'Tempo total na fase Diagnóstico (dias)', 'Tempo total na fase Montagem de proposta (dias)',
     'Tempo total na fase Apresentação de proposta (dias)', 'Tempo total na fase Negociação (dias)',
     'Tempo total na fase Renegociação (dias)']
].sum(axis=1).mean()

def todos_escolhidos(faturamento_total, total_vendas_ganhas, taxa_conversao, tempo_medio_fechamento):
    # Criar colunas para o título e gráficos
# Criar colunas para o título e gráficos
    col_title, col1, col2, col3 = st.columns([2, 1, 1, 1])

    with col_title:
        st.markdown(f"# Desempenho {ano_selecionado}")
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
                <div class="label">Média de fechamento</div> <div class="value">{tempo_medio_fechamento:,.2f} dias</div>
            </div>
            """, unsafe_allow_html=True)

    # Espaçamento entre as métricas e os gráficos
    st.markdown('<hr>', unsafe_allow_html=True)

    col4, col5 = st.columns(2)

    with col4:
        st.selectbox("Métrica", ['Quantidade', 'Faturamento'], key='metrica')        
        metrica = st.session_state['metrica']

        # Preparar os dados
        dados_metrica_vendedor = preparar_dados_metricas_vendedores(base_filtrada, metrica)

        # Exibir o gráfico
        dados_metrica_vendedor = dados_metrica_vendedor.reset_index(drop=True)
        if metrica == 'Quantidade':
            y_axis = alt.Y('Quantidade:Q', title='Quantidade')
        else:
            y_axis = alt.Y('Faturamento:Q', title='Faturamento (R$)')    

        st.altair_chart(alt.Chart(dados_metrica_vendedor).mark_bar().encode(x='Vendedor:N', y=y_axis)
            .properties(title=f"{metrica} por vendedor", width=400, height=400), use_container_width=True)

         # Ajuste do eixo X para rótulos horizontais e evitar sobreposição
        x_axis = alt.X(
            f'Vendedor:N',
            sort='-x',
            title='Vendedor',
            axis=alt.Axis(
                labelAngle=0,
                labelOverlap='greedy',
                labelExpr="length(datum.label) > 15 ? substring(datum.label, 0, 15) + '\\n' + substring(datum.label, 15) : datum.label"
            )
        )
    with col5:
        # Gráfico da taxa de conversão por vendedor
        taxa_conversao_vendedores = base_filtrada.groupby('Vendedor').apply(calcular_taxa_conversao).reset_index()
        taxa_conversao_vendedores.columns = ['Vendedor', 'Taxa de Conversão']
        st.altair_chart(alt.Chart(taxa_conversao_vendedores).mark_bar().encode(
        y=alt.Y('Vendedor:N', title='Vendedor', sort='-x'),
        x=alt.X('Taxa de Conversão:Q', title='Taxa de Conversão (%)'),
            tooltip=['Vendedor', 'Taxa de Conversão']
        ).properties(
        title="Taxa de Conversão por Vendedor",
        height=350
        ).interactive()
        )

        # Gráfico de pizza com a quantidade de negociações em cada fase
        fig = px.pie(base_filtrada, names='Fase atual', title='Quantidade de Negociações por Fase', width=400, height=400)
        st.plotly_chart(fig)


def vendedor_selecionados(faturamento_total, total_vendas_ganhas, taxa_conversao, tempo_medio_fechamento):
    # Criar colunas para o título e as métricas
    col_title, col1, col2, col3 = st.columns([4, 1.5, 1, 1.5])
    with col_title:
        st.markdown(f"# {vendedor_selecionado} {ano_selecionado}")
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
                <div class="label">Vendas Ganhas</div>
                <div class="value">{total_vendas_ganhas}</div>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric">
                <div class="label">Média de fechamento</div> <div class="value">{tempo_medio_fechamento:,.2f} dias</div>
            </div>
            """, unsafe_allow_html=True)

    # Espaçamento entre as métricas e os gráficos
    st.markdown('<hr>', unsafe_allow_html=True)

    col4, col5 = st.columns(2)

    with col4:
        st.write(f"# Leads de {vendedor_selecionado}")
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.selectbox("Situação", ['Ativo', 'Geral'], key='situacao')
        with subcol2:
            st.selectbox("Selecione o Lead", base_filtrada['Empresa'].unique(), key='lead')

        situacao = st.session_state['situacao']
        lead = st.session_state['lead']
    # Filtrar a base de dados do vendedor selecionado
        base_vendedor = base_filtrada[base_filtrada['Vendedor'] == vendedor_selecionado]
        
        # Exibir as informações dos leads do vendedor
        st.dataframe(base_vendedor[['Fase atual', 'Empresa', 'Nome do cliente', 'Setor', 'Valor Final', 'Data de cadastro', 'Origem', 'Checklist vertical', 'Perfil de cliente']])

    with col5:
        # Gráfico de indicador com a taxa de conversão do vendedor selecionado
        taxa_conversao_vendedor = base_filtrada.groupby('Vendedor').apply(calcular_taxa_conversao).reset_index()
        # Mondando gráfico 
        fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=taxa_conversao,
        title={'text': f" Taxa de Conversão de {vendedor_selecionado}",
               'font': {'size': 24, 'weight': 'bold'},
                'align': 'center'},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "rgba(0, 0, 0, 0)", 'showticklabels': False},
            'bar': {'color': "darkblue",  'thickness': 1},
            'bgcolor': "white",
            'borderwidth': 0,    
        }
        ))
        # Ajustando o layout para definir width e height
        fig.update_layout(
            width=390,  # Largura do gráfico
            height=250,  # Altura do gráfico
            margin={'t': 60},
        )

        # Exibindo o gráfico de conversão
        st.plotly_chart(fig)
        # Placeholder para o título dinâmico 
        title_placeholder = st.empty()  

        subcol1, subcol2 = st.columns(2)

        with subcol1:
            categoria = st.selectbox("Selecione a Categoria", ['Origem', 'Setor', 'Checklist vertical', 'Perfil de cliente'])
             # Contando quantas vezes cada valor da categoria aparece
            categoria_count = base_filtrada[categoria].value_counts().reset_index()
            categoria_count.columns = [categoria, 'Quantidade']
            # Atualiza o título dinamicamente baseado na seleção do selectbox 
            title_placeholder.markdown(f"### Análise dos leads por {categoria}")
            
            # Criando o gráfico de pizza com base na contagem
        fig = px.pie(categoria_count, names=categoria, values='Quantidade', 
               )

        # Exibindo o gráfico no Streamlit
        st.plotly_chart(fig)



if vendedor_selecionado == 'Todos':
    todos_escolhidos(faturamento_total, total_vendas_ganhas, taxa_conversao, tempo_medio_fechamento)
else:
    vendedor_selecionados(faturamento_total, total_vendas_ganhas, taxa_conversao, tempo_medio_fechamento)

