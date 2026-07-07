from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
CORS(app)

def conectar_db():
    conexao = sqlite3.connect('backend/estetica.db')
    conexao.row_factory = sqlite3.Row
    return conexao

# --- ROTAS DO CLIENTE ---
@app.route('/api/servicos', methods=['GET'])
def listar_servicos():
    conexao = conectar_db()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM Servicos WHERE status_ativo = 1")
    servicos = [dict(linha) for linha in cursor.fetchall()]
    conexao.close()
    return jsonify({"servicos": servicos})

@app.route('/api/horarios-livres', methods=['GET'])
def buscar_horarios():
    data_escolhida = request.args.get('data')
    id_servico = int(request.args.get('id_servico', 1))

    conexao = conectar_db()
    cursor = conexao.cursor()

    # Descobre a duração do serviço
    cursor.execute("SELECT duracao_minutos FROM Servicos WHERE id_servico = ?", (id_servico,))
    resultado = cursor.fetchone()
    duracao = resultado['duracao_minutos'] if resultado else 30

    # Busca as marcações e bloqueios daquele dia
    cursor.execute("SELECT data_hora_inicio, data_hora_fim FROM Agendamentos WHERE date(data_hora_inicio) = ?", (data_escolhida,))
    marcacoes_do_dia = cursor.fetchall()

    # NOVO: Busca os horários dinâmicos da tabela de Disponibilidade
    cursor.execute("SELECT hora_inicio, hora_fim, tipo_regra FROM Disponibilidade")
    regras = cursor.fetchall()
    conexao.close()

    # Valores padrão (caso ainda não tenha configurado no painel)
    str_abertura, str_fecho = "09:00", "18:00"
    str_almoco_inicio, str_almoco_fim = "13:00", "14:00"

    for regra in regras:
        if regra['tipo_regra'] == 'trabalho':
            str_abertura = regra['hora_inicio']
            str_fecho = regra['hora_fim']
        elif regra['tipo_regra'] == 'bloqueio':
            str_almoco_inicio = regra['hora_inicio']
            str_almoco_fim = regra['hora_fim']

    hora_abertura = datetime.strptime(str_abertura, "%H:%M")
    hora_fecho = datetime.strptime(str_fecho, "%H:%M")
    almoco_inicio = datetime.strptime(str_almoco_inicio, "%H:%M")
    almoco_fim = datetime.strptime(str_almoco_fim, "%H:%M")

    horarios_livres = []
    hora_atual = hora_abertura

    # Calcula a disponibilidade da agenda impedindo sobreposição e respeitando o almoço configurado
    while hora_atual + timedelta(minutes=duracao) <= hora_fecho:
        hora_fim_estimada = hora_atual + timedelta(minutes=duracao)
        bate_no_almoco = (hora_atual < almoco_fim and hora_fim_estimada > almoco_inicio)
        
        conflito_agenda = False
        for m in marcacoes_do_dia:
            m_inicio = datetime.strptime(m['data_hora_inicio'].split(" ")[:5], "%H:%M")
            m_fim = datetime.strptime(m['data_hora_fim'].split(" ")[:5], "%H:%M")
            if hora_atual < m_fim and hora_fim_estimada > m_inicio:
                conflito_agenda = True
                break

        if not bate_no_almoco and not conflito_agenda:
            horarios_livres.append(hora_atual.strftime("%H:%M"))

        hora_atual += timedelta(minutes=30)

    return jsonify({"horarios_disponiveis": horarios_livres})

@app.route('/api/agendar', methods=['POST'])
def agendar_servico():
    dados = request.get_json()
    nome = dados.get('nome')
    telefone = dados.get('telefone')
    id_servico = dados.get('id_servico')
    data = dados.get('data')
    horario = dados.get('horario')

    conexao = conectar_db()
    cursor = conexao.cursor()

    cursor.execute("INSERT INTO Clientes (nome, telefone_whatsapp) VALUES (?, ?)", (nome, telefone))
    id_cliente = cursor.lastrowid

    cursor.execute("SELECT duracao_minutos FROM Servicos WHERE id_servico = ?", (id_servico,))
    duracao = cursor.fetchone()['duracao_minutos']

    inicio_str = f"{data} {horario}:00"
    inicio_dt = datetime.strptime(inicio_str, "%Y-%m-%d %H:%M:%S")
    fim_dt = inicio_dt + timedelta(minutes=duracao)

    cursor.execute('''
        INSERT INTO Agendamentos (id_cliente, id_servico, data_hora_inicio, data_hora_fim, status)
        VALUES (?, ?, ?, ?, 'confirmado')
    ''', (id_cliente, id_servico, inicio_dt.strftime("%Y-%m-%d %H:%M:%S"), fim_dt.strftime("%Y-%m-%d %H:%M:%S")))

    conexao.commit()
    conexao.close()
    return jsonify({"mensagem": f"Sucesso! O agendamento de {nome} foi gravado."}), 201

# --- ROTAS DA ADMINISTRADORA ---
@app.route('/api/admin/agendamentos', methods=['GET'])
def listar_agendamentos():
    conexao = conectar_db()
    cursor = conexao.cursor()
    cursor.execute('''
        SELECT a.id_agendamento, IFNULL(c.nome, 'Bloqueio Manual') as nome, 
               c.telefone_whatsapp, IFNULL(s.nome_servico, 'Pausa / Imprevisto') as nome_servico,
               a.data_hora_inicio, a.data_hora_fim, a.status
        FROM Agendamentos a
        LEFT JOIN Clientes c ON a.id_cliente = c.id_cliente
        LEFT JOIN Servicos s ON a.id_servico = s.id_servico
        ORDER BY a.data_hora_inicio ASC
    ''')
    agendamentos = [dict(linha) for linha in cursor.fetchall()]
    conexao.close()
    return jsonify({"agendamentos": agendamentos})

@app.route('/api/admin/bloquear', methods=['POST'])
def bloquear_horario():
    dados = request.get_json()
    data = dados.get('data')
    hora_inicio = dados.get('hora_inicio')
    hora_fim = dados.get('hora_fim')

    inicio_dt = f"{data} {hora_inicio}:00"
    fim_dt = f"{data} {hora_fim}:00"

    conexao = conectar_db()
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO Agendamentos (id_cliente, id_servico, data_hora_inicio, data_hora_fim, status)
        VALUES (NULL, NULL, ?, ?, 'bloqueado')
    ''', (inicio_dt, fim_dt))
    conexao.commit()
    conexao.close()
    return jsonify({"mensagem": "Horário bloqueado com sucesso!"}), 201

# --- ROTAS DE SERVIÇOS ---
@app.route('/api/admin/servicos', methods=['POST'])
def criar_servico():
    dados = request.get_json()
    conexao = conectar_db()
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO Servicos (nome_servico, duracao_minutos, preco, status_ativo)
        VALUES (?, ?, ?, 1)
    ''', (dados['nome'], dados['duracao'], dados['preco']))
    conexao.commit()
    conexao.close()
    return jsonify({"mensagem": "Novo serviço criado com sucesso!"}), 201

@app.route('/api/admin/servicos/<int:id_servico>', methods=['PUT'])
def atualizar_servico(id_servico):
    dados = request.get_json()
    conexao = conectar_db()
    cursor = conexao.cursor()
    cursor.execute('''
        UPDATE Servicos SET nome_servico = ?, duracao_minutos = ?, preco = ?
        WHERE id_servico = ?
    ''', (dados['nome'], dados['duracao'], dados['preco'], id_servico))
    conexao.commit()
    conexao.close()
    return jsonify({"mensagem": "Serviço atualizado com sucesso!"}), 200

@app.route('/api/admin/servicos/<int:id_servico>', methods=['DELETE'])
def excluir_servico(id_servico):
    conexao = conectar_db()
    cursor = conexao.cursor()
    cursor.execute('''
        UPDATE Servicos SET status_ativo = 0
        WHERE id_servico = ?
    ''', (id_servico,))
    conexao.commit()
    conexao.close()
    return jsonify({"mensagem": "Serviço excluído com sucesso do seu catálogo!"}), 200

# --- NOVAS ROTAS: CONFIGURAÇÃO DE DISPONIBILIDADE ---
@app.route('/api/admin/disponibilidade', methods=['GET'])
def obter_disponibilidade():
    conexao = conectar_db()
    cursor = conexao.cursor()
    cursor.execute("SELECT tipo_regra, hora_inicio, hora_fim FROM Disponibilidade")
    regras = [dict(linha) for linha in cursor.fetchall()]
    conexao.close()
    return jsonify({"regras": regras})

@app.route('/api/admin/disponibilidade', methods=['POST'])
def salvar_disponibilidade():
    dados = request.get_json()
    conexao = conectar_db()
    cursor = conexao.cursor()
    
    # Limpa as configurações antigas para regravar as novas
    cursor.execute("DELETE FROM Disponibilidade")
    
    # Grava o horário de trabalho
    cursor.execute("INSERT INTO Disponibilidade (dia_semana, hora_inicio, hora_fim, tipo_regra) VALUES (0, ?, ?, 'trabalho')", 
                   (dados['abertura'], dados['fecho']))
    
    # Grava o horário de almoço (bloqueio fixo)
    cursor.execute("INSERT INTO Disponibilidade (dia_semana, hora_inicio, hora_fim, tipo_regra) VALUES (0, ?, ?, 'bloqueio')", 
                   (dados['almoco_inicio'], dados['almoco_fim']))
    
    conexao.commit()
    conexao.close()
    return jsonify({"mensagem": "Configurações de horário guardadas com sucesso!"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)