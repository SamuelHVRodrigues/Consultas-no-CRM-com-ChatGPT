"""
Descrição:
    Código feito usando a função assistants da API do gpt, consumindo o modelo gpt-4o-mini para responder perguntas sobre
a base de dados do CRM de comercial do CITi. Esse código está criando uma interface usando streamlit para que o usuário
consiga interagir e fazer as perguntas por lá. 

Resultados:
    Aparentemente está tendo bons resultados, as respostas costumam ser corretas para as perguntas. Porém, a pergunta 
feita pelo usuário precisa especificar bem o que ele deseja. Além disso, não está no formato de chat, ou seja, não é
possível continuar a conversa mantendo o contexto das mensagens anteriores e também está com um gasto muito elevado.

Próximos passos:
    - Entender melhor a função de assistants da API do gpt. https://platform.openai.com/docs/assistants/overview
    - Identificar o motivo do alto custo e diminuir.
    - Revisar e melhorar os prompts.
    - Transformar num formato de chat no qual as mensagens enviadas e recebidas sejam printadas na tela (igual o formato do gpt).

Cuidados necessários:
    - Monitorar continuamente o gasto através do site https://platform.openai.com/usage.
    - Não disponibilizar a chave de acesso para terceiros.
"""


# Importando bibliotecas
import streamlit as st
import openai
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import time

# Carregar variáveis de ambiente
_ = load_dotenv(find_dotenv())

client = openai.Client()

# Variável global para armazenar o assistente
if 'assistant_id' not in st.session_state:
    st.session_state.assistant_id = None

# Carregar a base de dados que foi tratada em outro arquivo
df = pd.read_csv(r'df_CRM.csv')

# Converter para datetime
df['Data de cadastro'] = pd.to_datetime(df['Data de cadastro'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
df['Primeira vez que entrou na fase Ganho'] = pd.to_datetime(df['Primeira vez que entrou na fase Ganho'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

# Passar o arquivo da base de dados para a openai
if 'file_id' not in st.session_state:
    file = client.files.create(
        file=open(r'df_CRM.csv', 'rb'),
        purpose='assistants'
    )
    st.session_state.file_id = file.id
else:
    file_id = st.session_state.file_id

# Criar assistant apenas se ainda não foi criado
if not st.session_state.assistant_id:
    assistant = client.beta.assistants.create(
        name='Consultor CRM de vendas CITi',
        instructions='Você é um especialista nas informações de negociações e vendas do CITi \
            , empresa júnior de tecnologia do Centro de Informática da UFPE. Você deve usar os \
            dados informados, que estão em csv, relativos às oportunidades de vendas do CITi para responder às perguntas'
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
            'Essa estrutura permite acompanhar o andamento das oportunidades de venda e identificar potenciais gargalos no processo comercial.',
        tools=[{'type': 'code_interpreter'}],
        tool_resources={'code_interpreter': {'file_ids': [st.session_state.file_id]}},
        model='gpt-4o-mini'
    )
    st.session_state.assistant_id = assistant.id  # Salva o ID do assistente
else:
    assistant_id = st.session_state.assistant_id

# Título da aplicação
st.title("Interface para Perguntas sobre a Base de Dados")

# Cria a thread apenas uma vez
if 'thread_id' not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
else:
    thread_id = st.session_state.thread_id

# Campo de texto para o usuário fazer uma pergunta
texto_mensagem = st.text_input("Faça sua pergunta sobre a base de dados:")

# Verifica se o usuário inseriu uma pergunta antes de prosseguir
if texto_mensagem:
    # Adiciona mensagem à thread existente
    message = client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role='user',
        content=texto_mensagem
    )
    
    # Roda a thread no assistant existente
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=st.session_state.assistant_id,
        instructions=''
    )
    
    # Define um timeout de 30 segundos e o tempo de espera entre verificações
    start_time = time.time()
    timeout = 100  # tempo máximo de espera em segundos
    wait_time = 4  # tempo de espera entre cada verificação em segundos
    
    # Aguarda a thread rodar com limite de tempo
    while run.status in ['queued', 'in_progress', 'cancelling']:
        time.sleep(wait_time)
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )
        
        # Verifica se o tempo de execução excedeu o timeout
        if time.time() - start_time > timeout:
            st.error("Tempo de execução excedido. Tente novamente mais tarde.")
            break

    if run.status == 'completed':
        mensagens = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
        st.subheader("Resposta:")
        st.write(mensagens.data[0].content[0].text.value)
    elif run.status == 'in_progress':
        st.subheader("Erro na execução:")
        st.write('O processamento demorou mais do que o esperado.')
    else:
        st.subheader("Erro na execução:")
        st.write('Erro:', run.status)
else:
    st.warning("Por favor, insira uma pergunta antes de enviar.")
