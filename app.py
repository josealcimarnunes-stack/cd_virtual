import os
import sqlite3
from flask import Flask, jsonify, render_template, request

# Importação dos Blueprints modulares
from rotas.compras import compras_bp  # <- Módulo de Compras & Suprimentos
from rotas.conferencia import conferencia_bp
from rotas.portaria import portaria_bp

app = Flask(__name__)

# ============================================================
# Inicialização e Configuração do Banco de Dados SQLite (Spare Parts)
# ============================================================
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


# Executa a criação da tabela ao iniciar o app
init_spare_parts_db()


# ============================================================
# Registro dos Blueprints (rotas modulares do CD Virtual)
# ============================================================
app.register_blueprint(portaria_bp)  # Portaria / Guarita
app.register_blueprint(conferencia_bp)  # Doca / Conferência Cega
app.register_blueprint(compras_bp)  # Compras & Suprimentos (Hub 3PL)


# ============================================================
# Rota para API de Peças Críticas (Manutenção / Spare Parts)
# ============================================================
@app.route("/api/pecas-criticas", methods=["GET"])
def listar_pecas_criticas():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pecas_criticas")
    rows = cursor.fetchall()
    conn.close()

    pecas = [dict(row) for row in rows]
    return jsonify(pecas)


# ============================================================
# Rota Principal - Planta Baixa do CD Virtual
# ============================================================
@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# Execução
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
