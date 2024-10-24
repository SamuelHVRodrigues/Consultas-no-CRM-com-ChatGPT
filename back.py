from flask import Flask, request, jsonify
import openai
from dotenv import load_dotenv, find_dotenv
import time
from utils import carregar_base

app = Flask(__name__) # Cria uma instância do Flask

MAX_TOKENS_OUTPUT = 500 # Define o número máximo de tokens que a resposta pode ter

df = carregar_base() # Carrega a base de dados diretamente do Google Sheets

# Salva o DataFrame como CSV temporariamente
csv_file_path = 'dados_oportunidades.csv'  # Define o caminho do arquivo CSV
df.to_csv(csv_file_path, index=False)  # Salva o DataFrame como CSV

_ = load_dotenv(find_dotenv()) # Carrega variáveis de ambiente do arquivo .env, se existir

client = openai.Client() # Cria uma instância do client da OpenAI

# Faz o upload do arquivo para a API da OpenAI
file = client.files.create(
    file=open(csv_file_path, 'rb'), # Abre o arquivo CSV em modo leitura binária
    purpose='assistants' # Define que o propósito do arquivo é para o assistant
)
file_id = file.id  # Salva o ID do arquivo

# Cria o assistant na API da OpenAI
assistant = client.beta.assistants.create(
    name='Consultor CRM de vendas CITi',
    instructions="Você deve usar os dados informados, que estão em csv, relativos às oportunidades de vendas do CITi para responder às perguntas."
"Colunas:"
"- Fase atual: Indica em qual fase do processo de vendas a oportunidade se encontra (Perdido, Renegociação, Ganho, Leads não-qualificados, Negociação, Montagem de proposta, Diagnóstico, Apresentação de proposta, Base de prospects, Qualificação)."
"- Data de cadastro: Data e hora em que a oportunidade foi registrada."
"- Nome do cliente: Nome da pessoa responsável pelo contato pelo lado do cliente."
"- Empresa: Nome da empresa do cliente."
"- Vendedor: Nome do colaborador da nossa empresa responsável pela oportunidade (vendedor responsável)."
"- Perfil de cliente: Tipo de cliente (Empresa consolidada, Startup, Empreendedor, Empresas Juniores, Grupo de pesquisa)."
"- Setor: Indústria ou setor em que o cliente atua (Energia e Sustentabilidade, Saúde e Cuidados Médicos, Ciências e Inovação, Transporte e Logística, Tecnologia da Informação (TI), entre outros)."
"- Checklist vertical: Tipo de serviço solicitado pelo cliente (Desenvolvimento Web, Concepção, Construção de API, entre outros)."
"Obs: Nesse campo de Checklist vertical pode aparecer mais de um tipo de serviço junto (para o caso do cliente querer mais de uma coisa)."
"- Origem: Canal de origem do lead (Marketing, Indicação de Ej, UFPE, Indicação MEJ, Parcerias, Ex cliente, Comunidade CITi, Prospecção Ativa, CIn, Porto Digital, Membre do CITi, Eventos, Renegociação)."
"- Valor Final: Valor final da proposta."
"- Motivo da perda: Razão pela qual a oportunidade foi perdida, se aplicável."
"- Motivo da não qualificação: Razão pela qual o lead não foi qualificado, se aplicável."
"- Tempo total na fase Base de prospects (dias): Quantidade de tempo que a oportunidade permaneceu na fase inicial."
"- Tempo total nas outras fases: Colunas que indicam o tempo em dias que a oportunidade permaneceu em cada uma das fases (qualificação, diagnóstico, montagem de proposta, apresentação, negociação, renegociação)."
"- Primeira vez que entrou na fase Ganho: Indica quando a oportunidade foi marcada como 'Ganho', caso tenha ocorrido."
"Essa estrutura permite acompanhar o andamento das oportunidades de venda e identificar potenciais gargalos no processo comercial."
"- Entenda vendas como vendas concluídas, ou seja oportunidades que foram ganhas e faturamento como soma das vendas concluídas.",
    tools=[{'type': 'code_interpreter'}], # Define que o assistant usará a ferramenta de interpretação de código
    tool_resources={'code_interpreter': {'file_ids': [file_id]}}, # Associa o arquivo carregado à ferramenta de interpretação de código
    model='gpt-4o-mini' # Especifica o modelo a ser utilizado
)
assistant_id = assistant.id # Salva o ID do assistant

thread = client.beta.threads.create() # Cria uma nova thread para interação com o assistant
thread_id = thread.id # Salva o ID da thread

# Requisição para a API da OpenAI
@app.route("/ask", methods=["POST"]) # Define a rota /ask que aceita requisições POST
def ask_openai(): # Define a função que será chamada quando a rota for acessada
    data = request.json # Obtém os dados da requisição no formato JSON
    question = data.get("question", "") # Extrai a pergunta do JSON ou define com string vazia se a pergunta não existir
    
    if question: # Verifica se a pergunta não está vazia
        # Adiciona mensagem à uma thread existente
        message = client.beta.threads.messages.create(
            thread_id=thread_id, # ID da thread que a mensagem será enviada
            role='user', # Define o papel da mensagem como 'user'
            content=question # Define o conteúdo da mensagem como a pergunta que foi obtida da requisição
        )

        # Cria uma nova execução para processar a pergunta
        run = client.beta.threads.runs.create(
            thread_id = thread_id, # ID da thread associada
            assistant_id = assistant_id, # ID do assistant que irá responder
            instructions='', # Instruções adicionais
            max_completion_tokens=MAX_TOKENS_OUTPUT # Define o número máximo de tokens na resposta
        )

        start_time = time.time() # Armazena o horário atual para controle de timeout
        timeout = 100  # Define um tempo máximo de execução em segundos
        wait_time = 4  # Define um intervalo de espera entre cada verificação de status da execução em segundos

        # Aguarda a thread rodar com limite de tempo
        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(wait_time) # Espera o tempo definido antes de verificar o status novamente
            # Recupera o status da execução
            run = client.beta.threads.runs.retrieve(
                thread_id = thread_id, # ID da thread associada
                run_id = run.id # ID da execução
            )

            # Verifica se o tempo de execução excedeu o timeout
            if time.time() - start_time > timeout:
                print('Tempo de execução excedido. Tente novamente mais tarde.')
                break # Sai do loop

        # Verifica se a execução foi completada com sucesso
        if run.status == 'completed':
            # Lista todas as mensagens na thread
            messages = client.beta.threads.messages.list(
                thread_id = thread_id # ID da thread associada
            )

            # Capturar os tokens usados
            # tokens_usados = run.get('usage', {}).get('total_tokens', 'Não disponível')  # Pega o total de tokens usados
            tokens_usados = run.usage.completion_tokens # Obtém o número de tokens utilizados na resposta
            resposta = messages.data[0].content[0].text.value # Extrai a resposta

            # Retorna a resposta e o número de tokens utilizados no formato JSON
            return jsonify({'answer': resposta, 'tokens_usados': tokens_usados})
        # Se a execução ainda está em andamento
        elif run.status == 'in_progress':
            return jsonify({'answer': 'Erro na execução: O processamento demorou mais do que o esperado.'}) # Retorna a mensagem de erro no formato JSON
        # Se houve algum erro na execução
        else:
            answer = f"Erro na execução: Erro: {run.status}" # Define a mensagem de erro
            return jsonify({'answer': answer}) # Retorna a mensagem de erro no formato JSON
    # Se nenhuma pergunta foi fornecida
    else:
        return jsonify({"error": "Nenhuma pergunta fornecida"}), 400 # Retorna um erro 400

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":
    app.run(debug=True) # Inicia o servidor Flask em mode de debug



