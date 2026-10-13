import sqlite3
from flask import Blueprint, jsonify

pecas_bp = Blueprint("pecas_bp", __name__)

DB_PATH = "cd_virtual.db"


def init_spare_parts_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pecas_criticas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_peca TEXT NOT NULL,
            categoria_equipamento TEXT NOT NULL,
            fornecedor TEXT NOT NULL,
            contato_suporte TEXT NOT NULL,
            preco_estimado REAL NOT NULL,
            lead_time_horas INTEGER NOT NULL,
            criticidade TEXT NOT NULL
        )
    """)

    # Insere dados padrão de peças críticas se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM pecas_criticas")
    if cursor.fetchone()[0] == 0:
        pecas_iniciais = [
            (
                "Robô Paletizador (Placa CPU/Sensor)",
                "Automação / Robótica",
                "Fanuc Automation Brasil",
                "(11) 3000-4455",
                19500.00,
                24,
                "Crítico",
            ),
            (
                "Motor Trifásico Principal (Esteira Doca)",
                "Eletromecânica",
                "WEG Indústrias S.A.",
                "(47) 3276-4000",
                12800.00,
                24,
                "Crítico",
            ),
            (
                "Redutor Planetário de Alta Carga",
                "Transmissão / Esteiras",
                "SEW-Eurodrive Brasil",
                "(19) 3835-8000",
                28500.00,
                48,
                "Crítico",
            ),
            (
                "Compressor de Parafuso (Ar Comprimido)",
                "Pneumática",
                "Schulz Compressores",
                "(47) 3451-6000",
                35000.00,
                12,
                "Crítico",
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO pecas_criticas (nome_peca, categoria_equipamento, fornecedor, contato_suporte, preco_estimado, lead_time_horas, criticidade)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            pecas_iniciais,
        )
        conn.commit()
    conn.close()


# Executa a criação da tabela ao importar o módulo
init_spare_parts_db()


@pecas_bp.route("/api/pecas-criticas", methods=["GET"])
def listar_pecas_criticas():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pecas_criticas")
    rows = cursor.fetchall()
    conn.close()

    pecas = [dict(row) for row in rows]
    return jsonify(pecas)
