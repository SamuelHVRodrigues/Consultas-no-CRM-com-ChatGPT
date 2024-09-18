import streamlit as st
import openai
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import tiktoken

# Carregar variáveis de ambiente
_ = load_dotenv(find_dotenv())

client = openai.Client()

# Carregar a base de dados que foi tratada em outro aquivo
df = pd.read_pickle('base_CRM')

# Título da aplicação
st.title("Interface para Perguntas sobre a Base de Dados")

# Campo de texto para o usuário fazer uma pergunta
user_input = st.text_input("Faça sua pergunta sobre a base de dados:")

# Função para converter o DataFrame para texto (limite de linhas e colunas, se necessário)
def df_para_string(df, max_linhas=500, max_colunas=25):
    return df.head(max_linhas).to_string(index=False, max_cols=max_colunas)

# Função para calcular o número de tokens
def calcular_tokens(texto):
    enc = tiktoken.encoding_for_model('gpt-4o-mini')  # Escolha o encoding para o modelo
    tokens = enc.encode(texto)
    return len(tokens)

# Função para fazer a requisição à API GPT
def obter_resposta(pergunta):
    
    # Convertendo o DataFrame para texto
    dados_df = df_para_string(df)
    
    mensagens = [
    {
        'role': 'user',
        'content': (
            f'Responda a seguinte pergunta: "{pergunta}" '
            f'Você deve acessar os dados contidos na seguinte base de dados: {dados_df} e a partir deles, realizar '
            'as operações que forem necessárias e retornar uma resposta precisa para a pergunta em questão.'
            '(consulte os dados presentes na base fornecida e responda de maneira específica, ou seja, '
            'com a resposta final e não com o caminho pra obter a resposta)'
            'Contexto da base de dados fornecida:\n'
            'Essa base de dados fornecida se trata da base de dados extraída do CRM de vendas da nossa empresa, '
            'o CITi (Centro Integrado de Tecnologia da Informação), empresa júnior do Centro de Informática da UFPE. '
            'Seguem informações sobre a base de dados:\n\n'
            'Descrição Geral:\n'
            'A base de dados armazena informações sobre o status de oportunidades comerciais, incluindo o nome dos clientes, '
            'as empresas envolvidas, os responsáveis pelo acompanhamento (vendedores), além de detalhes sobre o progresso em '
            'diferentes fases do ciclo de vendas (qualificação, diagnóstico, montagem de proposta, negociação, etc.). '
            'Também são incluídos dados sobre a origem do lead, motivo de perdas e tempos em cada fase.\n\n'
            'Colunas:\n'
            '- Fase atual: Indica em qual fase do processo de vendas a oportunidade se encontra (Perdido, Renegociação, Ganho,'
            'Leads não-qualificados, Negociação, Montagem de proposta, Diagnóstico, Apresentação de proposta, Base de prospects,' 
            'Qualificação).\n'
            '- Data de cadastro: Data e hora em que a oportunidade foi registrada.\n'
            '- Nome do cliente: Nome da pessoa responsável pelo contato pelo lado do cliente.\n'
            '- Empresa: Nome da empresa do cliente.\n'
            '- Vendedor: Nome do colaborador da nossa empresa responsável pela oportunidade (vendedor responsável).\n'
            '- Perfil de cliente: Tipo de cliente (Empresa consolidada, Startup, Empreendedor, Empresas Juniores, Grupo de pesquisa).\n'
            '- Setor: Indústria ou setor em que o cliente atua (Energia e Sustentabilidade, Saúde e Cuidados Médicos, Ciências e Inovação' 
            'Transporte e Logística, Tecnologia da Informação (TI), entre outros).\n'
            '- Checklist vertical: Tipo de serviço solicitado pelo cliente (Desenvolvimento Web, Concepção, Construção de API, entre outros)'
            'Obs: Nesse campo de Checklist vertical pode aparecer mais de um tipo de serviço junto (para o caso do cliente querer mais de uma coisa).\n'
            '- Origem: Canal de origem do lead (Marketing, Indicação de Ej, UFPE, Indicação MEJ, Parcerias, Ex cliente, Comunidade CITi, Prospecção Ativa' 
            'CIn, Porto Digital, Membre do CITi, Eventos, Renegociação).\n'
            '- Valor Final: Valor final da proposta.\n'
            '- Motivo da perda: Razão pela qual a oportunidade foi perdida, se aplicável.\n'
            '- Motivo da não qualificação: Razão pela qual o lead não foi qualificado, se aplicável.\n'
            '- Tempo total na fase Base de prospects (dias): Quantidade de tempo que a oportunidade permaneceu na fase inicial.\n'
            '- Tempo total nas outras fases: Colunas que indicam o tempo em dias que a oportunidade permaneceu em cada uma '
            'das fases (qualificação, diagnóstico, montagem de proposta, apresentação, negociação, renegociação).\n'
            '- Primeira vez que entrou na fase Ganho: Indica quando a oportunidade foi marcada como "Ganho", caso tenha ocorrido.\n\n'
            'Essa estrutura permite acompanhar o andamento das oportunidades de venda e identificar potenciais gargalos no processo comercial.'
        )
    }
]
    # Calcular tokens do input
    input_text = mensagens[0]['content']
    tokens_input = calcular_tokens(input_text)

    resposta = client.chat.completions.create(
        model='gpt-4-turbo',
        messages=mensagens,
        max_tokens=1000,
        temperature=0
    )

    # Calcular tokens da resposta
    tokens_resposta = calcular_tokens(resposta.choices[0].message.content)
    
    # Calcular o total de tokens
    total_tokens = tokens_input + tokens_resposta
    
    # Printar o número de tokens
    st.write(f"Número de tokens utilizados: {total_tokens}")
    
    return resposta.choices[0].message.content

# Quando o usuário submeter uma pergunta
if user_input:
    # Chama a função e exibe a resposta
    with st.spinner("Consultando a base de dados e a API..."):
        resposta_gpt = obter_resposta(user_input)
    st.subheader("Resposta:")
    st.write(resposta_gpt)

# Exibir os dados
st.subheader("Visualização da Base de Dados")
st.write(df)