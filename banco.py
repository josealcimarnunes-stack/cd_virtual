import sqlite3


def criar_banco():
    conn = sqlite3.connect("cd_virtual.db")
    cursor = conn.cursor()

    # Tabela de Endereços WMS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enderecos_wms (
            id_endereco INTEGER PRIMARY KEY AUTOINCREMENT,
            rua TEXT NOT NULL,
            predio INTEGER NOT NULL,
            nivel INTEGER NOT NULL,
            posicao INTEGER NOT NULL,
            tipo_area TEXT NOT NULL
        )
    """)

    # Tabela de Produtos (3 Categorias)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            exige_fefo BOOLEAN DEFAULT 0
        )
    """)

    # Tabela de Estoque
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id_estoque INTEGER PRIMARY KEY AUTOINCREMENT,
            id_produto INTEGER,
            id_endereco INTEGER,
            quantidade INTEGER NOT NULL,
            lote TEXT,
            data_validade TEXT,
            FOREIGN KEY(id_produto) REFERENCES produtos(id_produto),
            FOREIGN KEY(id_endereco) REFERENCES enderecos_wms(id_endereco)
        )
    """)

    # Tabela de Controle de Etapas e Status (Luzes de Controle)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS controle_simulacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            etapa TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL, -- 'VERDE', 'AMARELO', 'VERMELHO', 'BLOQUEADO'
            mensagem TEXT
        )
    """)

    # Inicializa as etapas zeradas
    etapas_iniciais = [
        ("portaria", "AMARELO", "Aguardando chegada de caminhão"),
        ("recebimento", "BLOQUEADO", "Aguardando liberação da portaria"),
        ("estoque", "BLOQUEADO", "Aguardando conferência de materiais"),
    ]
    cursor.executemany(
        """
        INSERT OR IGNORE INTO controle_simulacao (etapa, status, mensagem)
        VALUES (?, ?, ?)
    """,
        etapas_iniciais,
    )

    conn.commit()
    conn.close()
    print("✅ Banco de dados 'cd_virtual.db' criado e inicializado com sucesso!")


if __name__ == "__main__":
    criar_banco()
