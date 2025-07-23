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
    definir_colunas_tempo
)

# Configurações globais da página, incluindo o título, ícone do CITi, layout largo e estado inicial da barra lateral
st.set_page_config(layout="wide",
                   page_title="Desempenho Individual",
                   page_icon="assets/Logo.svg",
                   initial_sidebar_state="collapsed")

# Para poder ler o arquivo CSS para customizar a página
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


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


# Verificar se algum valor em 'Vendedor' tem mais de um vendedor (separados por vírgula)
base['Vendedor'] = base['Vendedor'].str.split(', ')
base = base.explode('Vendedor')  # Separar os vendedores em linhas individuais

# Manter apenas Nome e Sobrenome dos vendedores (separados por espaço)
base['Vendedor'] = base['Vendedor'].apply(lambda x: ' '.join(x.split()[:2]))
base_ganho['Vendedor'] = base_ganho['Vendedor'].apply(lambda x: ' '.join(x.split()[:2]))

# Sidebar para seleção do ano de acordo com as opções disponíveis 
anos_disponiveis = sorted(base_ganho['Ano'].dropna().unique(), reverse=True)
ano_selecionado = st.sidebar.radio("Selecione o ano:", anos_disponiveis)

# Filtrar a base geral pelo ano selecionado (só exibir informações daquele ano)
base_filtrada = base[base['Ano'] == int(ano_selecionado)]
# Filtrar base ganha pelo ano selecionado
base_filtrada_ganho = base_ganho[base_ganho['Ano'] == int(ano_selecionado)]


# Filtrar e ordenar os vendedores disponíveis
vendedores_disponiveis = sorted(base_filtrada['Vendedor']. #filtra a base por vendedor e ordena alfabeticamente
                                dropna(). # remove vendedores nulos
                                unique()) # remove duplicatas de vendedores

# Adicionar a opção 'Todos' como primeira escolha
vendedores_disponiveis = ['Todos'] + vendedores_disponiveis
# Sidebar com selectbox para seleção do vendedor
vendedor_selecionado = st.sidebar.selectbox("Selecione o vendedor:", list(vendedores_disponiveis))


# Filtrar a base e modificar o título de acordo com o vendedor selecionado
if vendedor_selecionado != 'Todos':
    base_filtrada = base_filtrada[base_filtrada['Vendedor'] == vendedor_selecionado]
    base_filtrada_ganho = base_filtrada_ganho[base_filtrada_ganho['Vendedor'] == vendedor_selecionado]

# Faturamento total, número de vendas ganhas e taxa de conversão
faturamento_total = base_filtrada_ganho['Valor Final'].sum()
total_vendas_ganhas = len(base_filtrada_ganho)
taxa_conversao = calcular_taxa_conversao(base_filtrada)

colunas_tempo = definir_colunas_tempo()
# Criação de uma nova coluna com a quantidade de dias que o lead permaneceu no funil 
base_filtrada_ganho['Quantidade de dias'] = (base_filtrada_ganho['Primeira vez que entrou na fase Ganho'] - base_filtrada_ganho['Criado em']).dt.days
# Cálculo do tempo médio de fechamento a partir da coluna criada e da função 'mean'
tempo_medio_fechamento = base_filtrada_ganho['Quantidade de dias'].mean()

# Para quando o tempo médio de fechamento for zero
tempo_medio_fechamento = tempo_medio_fechamento if tempo_medio_fechamento > 0 else 'Não consta'

# Função para exibir o desempenho geral, ou seja, quando a opção 'Todos' é selecionada
def todos_escolhidos(faturamento_total, total_vendas_ganhas, taxa_conversao, tempo_medio_fechamento):
# Criar colunas para o título e gráficos
    col_title, col1, col2, col3 = st.columns([2.5, 1, 1, 1])

    # Cálculo de Faturamento e Total de Vendas
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
                <div class="label">Tempo médio de fechamento </div> 
                <div class="value">{int(tempo_medio_fechamento)} dias</div>
            </div>
            """, unsafe_allow_html=True)

    # Espaçamento entre as métricas e os gráficos
    st.markdown('<hr>', unsafe_allow_html=True)

    col4, col5 = st.columns(2)

    with col4:
        # Criar uma selectbox para escolha da métrica
        st.selectbox("Defina a métrica", ['Quantidade', 'Faturamento'], key='metrica')        
        metrica = st.session_state['metrica']

        # Preparar os dados
        dados_metrica_vendedor = preparar_dados_metricas_vendedores(base_filtrada_ganho, metrica)

        # Exibir o gráfico
        dados_metrica_vendedor = dados_metrica_vendedor.reset_index(drop=True)
        if metrica == 'Quantidade':
            x_axis = alt.X('Quantidade:Q', title='Quantidade')
        else:
            x_axis = alt.X('Faturamento:Q', title='Faturamento (R$)')    

        # Ajuste do eixo Y para rótulos horizontais e evitar sobreposição
        y_axis = alt.Y(
            'Vendedor:N',
            sort='-x',
            title='Vendedor',
            axis=alt.Axis(
                labelAngle=0,
                labelOverlap='greedy',
                labelExpr="length(datum.label) > 15 ? substring(datum.label, 0, 15) + '\\n' + substring(datum.label, 15) : datum.label"
            )
        )

        # Gráfico de barras horizontais
        st.altair_chart(
            alt.Chart(dados_metrica_vendedor).mark_bar(color='#3f9c81').encode(y=y_axis, x=x_axis)
            .properties(title=f"{metrica} por vendedor", width=400, height=400), 
            use_container_width=True)
        

    with col5:
        # Gráfico da taxa de conversão por vendedor
        # Agrupa os dados da base filtrada por vendedor e aplica a função de cálculo de taxa de conversão a cada grupo.
        # Em seguida, reinicia o índice para transformar o índice 'Vendedor' em uma coluna.
        taxa_conversao_vendedores = base_filtrada.groupby('Vendedor').apply(calcular_taxa_conversao).reset_index()
        # Renomear as colunas do df resultante para 'Vendedor' e 'Taxa de Conversão', facilitando a leitura dos dados.
        taxa_conversao_vendedores.columns = ['Vendedor', 'Taxa de Conversão']
        
       # Filtrar os vendedores com taxa de conversão maior que 0
        taxa_conversao_vendedores_filtrada = taxa_conversao_vendedores[taxa_conversao_vendedores['Taxa de Conversão'] > 0]

        # Verificar se há dados para plotar e, caso tenha, exibir o gráfico
        if not taxa_conversao_vendedores_filtrada.empty:
            st.altair_chart(alt.Chart(taxa_conversao_vendedores_filtrada).mark_bar(color='#3f9c81').encode(
                x=alt.X('Vendedor:N', title='', sort='-y', axis=alt.Axis(labelAngle=0)),  # Rótulos dos vendedores na horizontal
                y=alt.Y('Taxa de Conversão:Q', title='Taxa de Conversão (%)', scale=alt.Scale(domain=[0, 100])),  # Garantir que vá até 100%
                tooltip=[alt.Tooltip('Vendedor:N'), alt.Tooltip('Taxa de Conversão:Q', format='.2f')]
            ).properties(
                title="Taxa de Conversão por Vendedor",
                height=245,  # Reduzindo a altura para economizar espaço
                width=565    # Aumentando a largura para melhor visualização
            ).interactive()
            )
        else:
            # Caso contrário, exibir uma mensagem de aviso
            st.info("Não há dados de taxa de conversão disponíveis para os vendedores selecionados.")


        # Gráfico de pizza com a quantidade de negociações em cada fase
        # Filtrar as fases com mais de 0 negociações e exibir o gráfico
        if not base_filtrada.empty:
            # Criar o gráfico
            fig = px.pie(base_filtrada, names='Fase atual', title='Panorama de negociações por Fase', 
                        color='Fase atual', color_discrete_sequence=px.colors.sequential.Blugrn_r, width=400, height=320)
            fig.update_layout(title_x=0.12,
                             legend=dict(
                            orientation="v",  # Coloca a legenda na vertical
                            yanchor="bottom",  # Ancla a legenda na parte inferior
                            xanchor="left",  # Ancla a legenda na parte esquerda
                            y=0.3,  # Centraliza verticalmente
                            x=0.68,  # Centraliza horizontalmente)
                        ))
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Caso contrário, exibir uma mensagem de aviso
            st.info("Não há dados de negociações para exibir o gráfico.")

# Função para exibir as métricas de um vendedor selecionado
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
                <div class="label">Tempo médio de fechamento</div> 
                <div class="value">{int(tempo_medio_fechamento)} dias</div>
            </div>
            """, unsafe_allow_html=True)

    # Espaçamento entre as métricas e os gráficos
    st.markdown('<hr>', unsafe_allow_html=True)

    col4, col5 = st.columns([1.25,1])
    # Filtrar a base de dados do vendedor selecionado
    base_vendedor = base_filtrada[base_filtrada['Vendedor'] == vendedor_selecionado]
    
    # Converter 'Criado em' para datetime, se ainda não estiver
    if not pd.api.types.is_datetime64_any_dtype(base_vendedor['Criado em']):
        base_vendedor['Criado em'] = pd.to_datetime(base_vendedor['Criado em'], errors='coerce')

    with col4:
        st.markdown(f"<h3 class='left-align'>Leads de {vendedor_selecionado}</h3>", unsafe_allow_html=True)

        # Subdividir a col4 em duas subcolunas
        subcol1, subcol2 = st.columns([1, 2])

        with subcol1:
            situacao = st.selectbox("Situação", ['Ativo', 'Geral'], key='situacao')
        
        # Filtrar com base na situação selecionada
        base_filtrada_situacao = base_vendedor.copy()
        # Caso a siuação seja 'Ativo', excluir registros onde a 'Fase atual' é 'Ganho', 'Perdido' ou 'Leads não-qualificados'
        if situacao == 'Ativo':
            base_filtrada_situacao = base_vendedor[~base_vendedor['Fase atual'].isin(['Ganho', 'Perdido', 'Leads não-qualificados'])]
        else:
            base_filtrada_situacao = base_vendedor  # Caso 'Geral', mantém todos os leads

        # Empresas filtradas com base na situação escolhida (em subcol2)
        # Filtra a lista 'empresas_filtradas', removendo entradas que estão vazias (dropna) ou contêm apenas espaços em branco (!= '').
        # Usa o método 'str.strip()' para remover espaços em branco antes de verificar se a entrada é uma string vazia.
        empresas_filtradas = base_filtrada_situacao['Empresa'].dropna()
        empresas_filtradas = empresas_filtradas[empresas_filtradas.str.strip() != '']
        
        with subcol2:
            # Selecionar o lead caso exista uma empresa disponível para a situação selecionada
            if len(empresas_filtradas) > 0:
                lead_selecionado = st.selectbox("Selecione o Lead", empresas_filtradas, key='lead')
            else:
                # Exibir uma mensagem de aviso caso nenhuma empresa seja disponível para a situação selecionada
                st.warning("Nenhuma empresa disponível para a situação selecionada.")
                lead_selecionado = None  # Definir como None para evitar erros posteriores
        
        if lead_selecionado:
            # Selecionar dados do lead selecionado, com base na coluna 'Empresa'
            lead_data = base_filtrada_situacao[base_filtrada_situacao['Empresa'] == lead_selecionado]
            # Se o conteúdo de 'lead_data' não estiver vazio
            if not lead_data.empty:
                # Calcular o tempo total no funil somando as colunas de dias
                lead_data['Criado em'] = pd.to_datetime(lead_data['Criado em'], errors='coerce')
                lead_data['Quantidade de dias no Funil'] =(pd.Timestamp('now') - lead_data['Criado em']).dt.days


            # Container com borda ao redor das colunas
            with st.container(border=True):

                # Subcolunas para dispor as informações do lead selecionado
                info_col1, info_col2 = st.columns(2)
                with info_col1:
                    st.markdown(f"""
                        <div class="metric">
                            <div class="label">Fase atual</div>
                            <div class="value">{lead_data['Fase atual'].values[0] if pd.notnull(lead_data['Fase atual'].values[0]) else 'Não consta'}</div> 
                        </div>
                        <div class="metric">
                            <div class="label">Setor</div>
                        <div class="value">{lead_data['Setor'].values[0].strip() if pd.notnull(lead_data['Setor'].values[0]) and lead_data['Setor'].values[0].strip() != '' else 'Não consta'}</div>
                        </div>
                        <div class="metric">
                            <div class="label">Origem</div>
                            <div class="value">{lead_data['Origem'].values[0].strip() if pd.notnull(lead_data['Origem'].values[0]) and lead_data['Origem'].values[0].strip() != '' else 'Não consta'}</div>
                        </div>
                            <div class="metric">
                            <div class="label">Tempo Total no Funil</div>
                            <div class="value">{lead_data['Quantidade de dias no Funil'].values[0]} dias</div>  
                        </div>
                        """, unsafe_allow_html=True)
                with info_col2:
                    st.markdown(f"""
                        <div class="metric">
                            <div class="label">Faturamento</div>
                            <div class="value">R$ {lead_data['Valor Final'].sum():,.2f}</div>
                        </div>
                            <div class="metric">
                            <div class="label">Data de cadastro</div>
                            <div class="value">{lead_data['Criado em'].dt.strftime('%d/%m/%Y').values[0] if pd.notnull(lead_data['Criado em'].values[0]) else 'Não consta'}</div> 
                        </div>
                            <div class="metric">
                            <div class="label">Perfil de cliente</div>
                            <div class="value">{lead_data['Perfil de cliente'].values[0].strip() if pd.notnull(lead_data['Perfil de cliente'].values[0]) and lead_data['Perfil de cliente'].values[0].strip() != '' else 'Não consta'}</div>
                        </div>
                            <div class="metric">
                            <div class="label">Serviço</div>
                            <div class="value">{lead_data['Serviço'].values[0].strip() if pd.notnull(lead_data['Serviço'].values[0]) and lead_data['Serviço'].values[0].strip() != '' else 'Não consta'}</div>
                        </div>
                        """, unsafe_allow_html=True)

            if lead_data.empty:
                st.warning("Dados do lead não encontrados.")

    with col5:
        # Agrupar a base de dados filtrada por vendedor e aplicar a função 'calcular_taxa_conversao' a cada grupo para calcular a taxa de conversão.
        # Em seguida, reiniciar o índice para transformar 'Vendedor' em uma coluna regular.
        taxa_conversao_vendedor = base_filtrada.groupby('Vendedor').apply(calcular_taxa_conversao).reset_index()
        # Renomear as colunas do df resultante para 'Vendedor' e 'Taxa de Conversão', facilitando a interpretação dos dados.
        taxa_conversao_vendedor.columns = ['Vendedor', 'Taxa de Conversão']
        
        # Criando subcolunas para garantir a disposição correta do gráfico
        subcol1, subcol2, subcol3 = st.columns([1,2.5,1])
        with subcol2:
        # Verificar se há dados para plotar o gráfico de indicador com a taxa de conversão do vendedor selecionado
            if not taxa_conversao_vendedor.empty:
                # Extrair a taxa de conversão do vendedor selecionado
                taxa_vendedor = taxa_conversao_vendedor[taxa_conversao_vendedor['Vendedor'] == vendedor_selecionado]['Taxa de Conversão'].values
                taxa_vendedor = taxa_vendedor[0] if len(taxa_vendedor) > 0 else 0

                # Criar o gráfico de indicador
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=taxa_vendedor,
                    title={'text': "Taxa de Conversão",
                        'font': {'size': 24, 'weight': 'bold'},
                            'align': 'center'},
                    number={'suffix': "%", 'font': {'size': 40, 'weight': 'bold'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "rgba(0, 0, 0, 0)", 'showticklabels': False},
                        'bar': {'color': "#266b6e",  'thickness': 1},
                        'bgcolor': "white",
                        'borderwidth': 0,    
                    }
                ))

                # Ajustando o layout para definir melhor o width (largura) e height (altura)
                fig.update_layout(
                    width=250,  # Largura do gráfico
                    height=200,  # Altura do gráfico
                    margin={'t': 0, 'b': 0, 'l':0, 'r':0},
                )

                # Plotando o gráfico
                st.plotly_chart(fig)
                
            else:
                # Caso nenhuma taxa de conversão seja encontrada, exibir uma mensagem de aviso
                st.info("Não há dados de taxa de conversão disponíveis para o vendedor selecionado.")

        # Criar um placeholder vazio na interface Streamlit, permitindo que um título seja inserido ou atualizado posteriormente. 
        # Isso permite que o título seja atualizado dinamicamente com base na seleção do selectbox.
        title_placeholder = st.empty()  

       # Colunas para o gráfico e o selectbox
        subcol1, subcol2 = st.columns([0.95,2])

        with subcol1:
            # Selectbox para escolha da categoria
            categoria = st.selectbox("Selecione a Categoria", ['Origem', 'Setor', 'Serviço', 'Perfil de cliente'], key='categoria')
            # Filtrar a base de dados para manter apenas os registros em que a coluna especificada por 'categoria' contém valores do tipo string e que não são compostos apenas por dígitos.
            # Usar 'apply' com uma função lambda que verifica se o valor é uma string e não é numérico.
            base_filtrada_categoria = base_filtrada[base_filtrada[categoria].apply(lambda x: isinstance(x, str) and not x.isdigit())]
        
            # Contando quantas vezes cada valor da categoria aparece
            categoria_count = base_filtrada_categoria[categoria].value_counts().reset_index()
            categoria_count.columns = [categoria, 'Quantidade']

            # Atualiza o placeholder 'title_placeholder' (que foi criado anteriormente, mas estava vazio) para exibir um título de acordo com a categoria selecionada 
            title_placeholder.markdown(f"#### Análise dos leads por {categoria}")

        with subcol2:     
            # Criando o gráfico de pizza se 'categoria_count' não estiver vazio
            if not categoria_count.empty:
                fig_categoria = px.pie(categoria_count, names=categoria, values='Quantidade',
                                        color_discrete_sequence=px.colors.sequential.Blugrn_r, width=510, height=320)
        fig_categoria.update_layout(
        legend=dict(
            bgcolor='rgba(0,0,0,0)',  # fundo transparente
            y=1.1,                   # posição da legenda abaixo do gráfico
            x=10,   
            xanchor='right',
            yanchor='top',
            orientation='h',
            font=dict(size=9),            
            
        ),
        margin=dict(l=15, r=0, t=0, b=50),
    )
            
        st.plotly_chart(fig_categoria)
                

# Executar a função apropriada com base na seleção do vendedor
if vendedor_selecionado == 'Todos':
    todos_escolhidos(faturamento_total, total_vendas_ganhas, taxa_conversao, tempo_medio_fechamento)
else:
    vendedor_selecionados(faturamento_total, total_vendas_ganhas, taxa_conversao, tempo_medio_fechamento)

