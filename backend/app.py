from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# 1. Catálogo de Serviços (Base de Dados Simulada)
SERVICOS = [
    {"id_servico": 1, "nome_servico": "Design Simples", "preco": 15, "duracao_minutos": 30},
    {"id_servico": 2, "nome_servico": "Design com Henna", "preco": 25, "duracao_minutos": 60}
]

# 2. Agenda Ocupada (Simulando que uma cliente já marcou um serviço de 1 hora hoje)
AGENDAMENTOS_EXISTENTES = [
    {"data": "2026-10-25", "hora_inicio": "14:00", "hora_fim": "15:00"}
]

@app.route('/api/servicos', methods=['GET'])
def listar_servicos():
    return jsonify({"servicos": SERVICOS})

@app.route('/api/horarios-livres', methods=['GET'])
def buscar_horarios():
    data_escolhida = request.args.get('data')
    id_servico = int(request.args.get('id_servico', 1))

    # A. Descobrir a duração dinâmica do serviço escolhido
    duracao = 30
    for s in SERVICOS:
        if s['id_servico'] == id_servico:
            duracao = s['duracao_minutos']
            break

    # B. Definir Horário de Funcionamento e Pausas
    hora_abertura = datetime.strptime("09:00", "%H:%M")
    hora_fecho = datetime.strptime("18:00", "%H:%M")
    almoco_inicio = datetime.strptime("13:00", "%H:%M")
    almoco_fim = datetime.strptime("14:00", "%H:%M")

    # C. Filtrar as marcações que já existem para a data escolhida
    marcacoes_do_dia = [a for a in AGENDAMENTOS_EXISTENTES if a['data'] == data_escolhida]

    horarios_livres = []
    hora_atual = hora_abertura

    # D. O Algoritmo: Percorrer o dia e testar encaixes
    while hora_atual + timedelta(minutes=duracao) <= hora_fecho:
        hora_fim_estimada = hora_atual + timedelta(minutes=duracao)

        # Regra 1: O serviço não pode calhar na hora de almoço
        bate_no_almoco = (hora_atual < almoco_fim and hora_fim_estimada > almoco_inicio)

        # Regra 2: Prevenção de conflitos com outras clientes
        conflito_agenda = False
        for m in marcacoes_do_dia:
            m_inicio = datetime.strptime(m['hora_inicio'], "%H:%M")
            m_fim = datetime.strptime(m['hora_fim'], "%H:%M")
            
            # Se os horários se cruzarem, detetamos um conflito
            if hora_atual < m_fim and hora_fim_estimada > m_inicio:
                conflito_agenda = True
                break

        # Se não houver conflitos e não for hora de almoço, o horário é válido!
        if not bate_no_almoco and not conflito_agenda:
            horarios_livres.append(hora_atual.strftime("%H:%M"))

        # Avançar o relógio de 30 em 30 minutos para testar a próxima vaga
        hora_atual += timedelta(minutes=30)

    return jsonify({"horarios_disponiveis": horarios_livres})

@app.route('/api/agendar', methods=['POST'])
def agendar_servico():
    dados = request.get_json()
    nome = dados.get('nome')
    print(f"Novo agendamento de {nome} processado com sucesso!")
    return jsonify({"mensagem": f"Sucesso! Agendamento de {nome} confirmado."}), 201

if __name__ == '__main__':
    app.run(debug=True)