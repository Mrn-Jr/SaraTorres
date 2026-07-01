from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
CORS(app)

# --------------------------------------------------------
# FUNÇÃO ESSENCIAL: A "ponte" para a Base de Dados
# --------------------------------------------------------
def conectar_db():
    conexao = sqlite3.connect('backend/estetica.db')
    conexao.row_factory = sqlite3.Row
    return conexao

# --------------------------------------------------------
# ROTAS DOS CLIENTES (Agendar e Ver Serviços)
# --------------------------------------------------------
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

    cursor.execute("SELECT duracao_minutos FROM Servicos WHERE id_servico = ?", (id_servico,))
    resultado = cursor.fetchone()
    duracao = resultado['duracao_minutos'] if resultado else 30

    cursor.execute("SELECT data_hora_inicio, data_hora_fim FROM Agendamentos WHERE date(data_hora_inicio) = ?", (data_escolhida,))
    marcacoes_do_dia = cursor.fetchall()
    conexao.close()

    hora_abertura = datetime.strptime("09:00", "%H:%M")
    hora_fecho = datetime.strptime("18:00", "%H:%M")
    almoco_inicio = datetime.strptime("13:00", "%H:%M")
    almoco_fim = datetime.strptime("14:00", "%H:%M")

    horarios_livres = []
    hora_atual = hora_abertura

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

# --------------------------------------------------------
# ROTA DA ADMINISTRADORA (Painel de Gestão)
# --------------------------------------------------------
@app.route('/api/admin/agendamentos', methods=['GET'])
def listar_agendamentos():
    conexao = conectar_db()
    cursor = conexao.cursor()
    
    cursor.execute('''
        SELECT a.id_agendamento, c.nome, c.telefone_whatsapp, s.nome_servico,
               a.data_hora_inicio, a.data_hora_fim, a.status
        FROM Agendamentos a
        JOIN Clientes c ON a.id_cliente = c.id_cliente
        JOIN Servicos s ON a.id_servico = s.id_servico
        ORDER BY a.data_hora_inicio ASC
    ''')
    
    agendamentos = [dict(linha) for linha in cursor.fetchall()]
    conexao.close()
    
    return jsonify({"agendamentos": agendamentos})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)