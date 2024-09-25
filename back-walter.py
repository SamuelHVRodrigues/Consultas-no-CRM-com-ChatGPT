from flask import Flask, request, jsonify
import openai
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import time

app = Flask(__name__)

# Carregar a base de dados que foi tratada em outro arquivo
df = pd.read_csv(r'df_CRM.csv')

# Carregar variáveis de ambiente
_ = load_dotenv(find_dotenv())

# Cria o client da openai
client = openai.Client()

# Definir limite de tokens de saída
MAX_TOKENS_OUTPUT = 150  # Exemplo: limite de 150 tokens de resposta

'''
O custo para o uso do modelo GPT-4o Mini é bastante acessível. Atualmente, os preços são os seguintes:

Tokens de entrada: $0.15 por milhão de tokens
Tokens de saída: $0.60 por milhão de tokens
'''

# Requisição para a API da OpenAI
@app.route("/ask", methods=["POST"])
def ask_openai():
    data = request.json
    question = data.get("question", "")
    
    if question:
        # Adiciona mensagem à thread existente
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role='user',
            content=question
        )

        # Roda a thread com limite de tokens de saída e usando o modelo gpt-4o-mini
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions=
"Você é um especialista nas informações de negociações e vendas do CITi, empresa júnior de tecnologia do Centro de Informática da UFPE."
"Você deve usar os dados informados, que estão em csv, relativos às oportunidades de vendas do CITi para responder às perguntas."
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
"Essa estrutura permite acompanhar o andamento das oportunidades de venda e identificar potenciais gargalos no processo comercial.",
            max_tokens=MAX_TOKENS_OUTPUT,  # Limitar o número de tokens de saída
            model="gpt-4o-mini"  # Define o modelo para gpt-4o-mini
        )

        # Define um timeout de 100 segundos e o tempo de espera entre verificações
        start_time = time.time()
        timeout = 100  # tempo máximo de espera em segundos
        wait_time = 4  # tempo de espera entre cada verificação em segundos

        # Aguarda a thread rodar com limite de tempo
        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(wait_time)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            # Verifica se o tempo de execução excedeu o timeout
            if time.time() - start_time > timeout:
                print('Tempo de execução excedido. Tente novamente mais tarde.')
                break

        # Verifica o status para dar o retorno
        if run.status == 'completed':
            messages = client.beta.threads.messages.list(
                thread_id=thread_id
            )
            
            # Capturar os tokens usados
            tokens_usados = run.get('usage', {}).get('total_tokens', 'Não disponível')  # Pega o total de tokens usados
            resposta = messages.data[0].content[0].text.value
            
            return jsonify({
                'answer': resposta,
                'tokens_usados': tokens_usados
            })
        elif run.status == 'in_progress':
            return jsonify({'answer': 'Erro na execução: O processamento demorou mais do que o esperado.'})
        else:
            answer = f"Erro na execução: Erro: {run.status}"
            return jsonify({'answer': answer})
    else:
        return jsonify({"error": "Nenhuma pergunta fornecida"}), 400

if __name__ == "__main__":
    app.run(debug=True)

