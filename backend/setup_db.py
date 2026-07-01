import sqlite3

def criar_banco_dados():
    # Vai criar um ficheiro chamado 'estetica.db' na pasta backend
    conexao = sqlite3.connect('backend/estetica.db')
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

    # 2. Tabela: Servicos (Catálogo)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Servicos (
            id_servico INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_servico TEXT NOT NULL,
            duracao_minutos INTEGER NOT NULL,
            preco REAL NOT NULL,
            status_ativo BOOLEAN DEFAULT 1
        )
    ''')

    # 3. Tabela: Agendamentos (A tabela central que gere o calendário)
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

    # 4. Tabela: Disponibilidade (Configuração da Administradora - Opcional)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Disponibilidade (
            id_regra INTEGER PRIMARY KEY AUTOINCREMENT,
            dia_semana INTEGER NOT NULL,
            hora_inicio TIME NOT NULL,
            hora_fim TIME NOT NULL,
            tipo_regra TEXT NOT NULL
        )
    ''')

    # 5. Inserir os serviços padrão para não começarmos com a base de dados vazia!
    # O comando 'IGNORE' evita duplicações se rodar o script duas vezes.
    cursor.execute("INSERT OR IGNORE INTO Servicos (id_servico, nome_servico, duracao_minutos, preco, status_ativo) VALUES (1, 'Design Simples', 30, 15.0, 1)")
    cursor.execute("INSERT OR IGNORE INTO Servicos (id_servico, nome_servico, duracao_minutos, preco, status_ativo) VALUES (2, 'Design com Henna', 60, 25.0, 1)")

    # Gravar as alterações e fechar
    conexao.commit()
    conexao.close()
    print("Banco de dados 'estetica.db' criado com sucesso com as tabelas: Clientes, Servicos, Agendamentos e Disponibilidade!")

if __name__ == '__main__':
    criar_banco_dados()