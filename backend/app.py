from flask import Flask, jsonify, request
from flask_cors import CORS  # <-- Adicione esta linha (Importa a permissão)

app = Flask(__name__)
CORS(app)  # <-- Adicione esta linha (Ativa a permissão no seu sistema

# -------------------------------------------------------------------
# ENDPOINT 1: Listar Serviços
# -------------------------------------------------------------------
@app.route('/api/servicos', methods=['GET'])
def listar_servicos():
    """
    Retorna a lista de serviços (ex: Design, Henna) com preços e tempos de duração [2].
    """
    # No futuro, estes dados virão do ficheiro database.py
    servicos_mock = [
        {"id_servico": 1, "nome_servico": "Design Simples", "duracao_minutos": 30, "preco": 15.00},
        {"id_servico": 2, "nome_servico": "Design com Henna", "duracao_minutos": 60, "preco": 25.00}
    ]
    return jsonify({"servicos": servicos_mock}), 200

# -------------------------------------------------------------------
# ENDPOINT 2: Buscar Horários Livres
# -------------------------------------------------------------------
@app.route('/api/horarios-livres', methods=['GET'])
def buscar_horarios():
    """
    Recebe uma data e o ID do serviço, e retorna os blocos de horas disponíveis no dia [2].
    """
    data = request.args.get('data')
    id_servico = request.args.get('id_servico')
    
    # Aqui chamaremos a lógica complexa do ficheiro algoritmos.py para cruzar 
    # a duração do serviço com a agenda livre do dia [1].
    # Por enquanto, devolvemos um exemplo estático para a interface funcionar:
    horarios_mock = ["14:00", "15:30", "17:00"]
    
    return jsonify({
        "data_solicitada": data,
        "id_servico": id_servico,
        "horarios_disponiveis": horarios_mock
    }), 200

# -------------------------------------------------------------------
# ENDPOINT 3: Efetuar Agendamento
# -------------------------------------------------------------------
@app.route('/api/agendar', methods=['POST'])
def agendar_servico():
    """
    Recebe os dados da cliente e grava o agendamento no banco de dados, bloqueando aquele espaço de tempo [2].
    """
    dados_cliente = request.json
    
    # Dados esperados do frontend: nome, telefone, id_servico, data, horario
    nome = dados_cliente.get('nome')
    telefone = dados_cliente.get('telefone')
    horario = dados_cliente.get('horario')
    
    # Aqui conectaremos com o database.py para gravar na tabela 'Agendamentos' e 'Clientes'.
    
    return jsonify({
        "status": "sucesso",
        "mensagem": f"Agendamento confirmado para {nome} às {horario}."
    }), 201

if __name__ == '__main__':
    # Inicia o servidor local na porta 5000
    app.run(debug=True, port=5000)