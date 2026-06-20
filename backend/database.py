import sqlite3

def conectar_bd():
    """Cria a conexão com o banco de dados SQLite."""
    # Isto criará um ficheiro chamado 'estetica.db' na sua pasta backend
    return sqlite3.connect('estetica.db')

def criar_tabelas():
    """Função para criar as 4 tabelas centrais do sistema."""
    conexao = conectar_bd()
    cursor = conexao.cursor()

    # 1. Tabela: Clientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone_whatsapp TEXT NOT NULL,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. Tabela: Servicos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Servicos (
        id_servico INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_servico TEXT NOT NULL,
        duracao_minutos INTEGER NOT NULL,
        preco DECIMAL NOT NULL,
        status_ativo BOOLEAN DEFAULT 1
    )
    ''')

    # 3. Tabela: Agendamentos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Agendamentos (
        id_agendamento INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cliente INTEGER,
        id_servico INTEGER,
        data_hora_inicio DATETIME NOT NULL,
        data_hora_fim DATETIME NOT NULL,
        status TEXT DEFAULT 'pendente',
        FOREIGN KEY (id_cliente) REFERENCES Clientes (id_cliente),
        FOREIGN KEY (id_servico) REFERENCES Servicos (id_servico)
    )
    ''')

    # 4. Tabela: Disponibilidade (Opcional/Configuração)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Disponibilidade (
        id_regra INTEGER PRIMARY KEY AUTOINCREMENT,
        dia_semana INTEGER NOT NULL,
        hora_inicio TIME NOT NULL,
        hora_fim TIME NOT NULL,
        tipo_regra TEXT NOT NULL
    )
    ''')

    conexao.commit()
    conexao.close()
    print("Base de dados e tabelas criadas com sucesso!")

if __name__ == '__main__':
    # Quando rodar este ficheiro, ele vai criar o banco de dados
    criar_tabelas()