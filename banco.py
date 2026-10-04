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
            status TEXT NOT NULL,
            mensagem TEXT
        )
    """)

    # Nova Tabela: Cenários de Portaria (Treinamento / Banco de Caminhões Bons e Ruins)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cenarios_portaria (
            id_cenario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cenario TEXT NOT NULL,
            placa TEXT NOT NULL,
            carreta TEXT NOT NULL,
            motorista TEXT NOT NULL,
            doc_motorista TEXT NOT NULL,
            transportadora TEXT NOT NULL,
            peso_bruto INTEGER NOT NULL,
            chk_lacre BOOLEAN NOT NULL,
            chk_bau BOOLEAN NOT NULL,
            chk_epis BOOLEAN NOT NULL,
            po TEXT NOT NULL,
            tipo_falha_esperada TEXT NOT NULL, -- 'ok', 'documento', 'placa', 'inspecao', 'fiscal'
            descricao_problema TEXT NOT NULL
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

    # Inicializa cenários de teste padrão na tabela de portaria
    cenarios_iniciais = [
        (
            "Caminhão Bom 01 - Tudo Conforme",
            "ABC-1234",
            "XYZ-9876",
            "Carlos Eduardo",
            "123.456.789-00",
            "Logística Brasil Express",
            42850,
            1,
            1,
            1,
            "PO-2026-9941",
            "ok",
            "Nenhum problema encontrado. Carga liberada.",
        ),
        (
            "Caminhão Ruim 01 - Lacre Violado",
            "ERR-4040",
            "BAD-1111",
            "Marcos Pneus",
            "111.222.333-44",
            "Veloz Cargas",
            39000,
            0,
            1,
            1,
            "PO-2026-9943",
            "inspecao",
            "Reprovado no checklist de segurança (Lacre danificado).",
        ),
        (
            "Caminhão Ruim 02 - Documento Faltando",
            "DEF-5678",
            "GHI-1234",
            "Ana sem CNH",
            "",
            "Express Falso",
            31000,
            1,
            1,
            1,
            "PO-2026-9944",
            "documento",
            "CPF/CNH do motorista ausente ou inválido.",
        ),
    ]
    cursor.executemany(
        """
        INSERT OR IGNORE INTO cenarios_portaria (nome_cenario, placa, carreta, motorista, doc_motorista, transportadora, peso_bruto, chk_lacre, chk_bau, chk_epis, po, tipo_falha_esperada, descricao_problema)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        cenarios_iniciais,
    )

    conn.commit()
    conn.close()
    print(
        "✅ Banco de dados 'cd_virtual.db' criado e atualizado com cenários de"
        " portaria!"
    )


if __name__ == "__main__":
    criar_banco()
