from datetime import timedelta
import os
import sqlite3
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

# Importação dos Blueprints modulares
from rotas.arquivo import arquivo_bp
from rotas.compras import compras_bp
from rotas.conferencia import conferencia_bp
from rotas.portaria import portaria_bp

app = Flask(__name__)

app.secret_key = "logisuprimentos_secret_key_2026"


# ============================================================
# TRAVA DE SEGURANÇA GLOBAL REFORÇADA
# ============================================================
@app.before_request
def verificar_autenticacao():
    rotas_livres = ["login", "static"]

    if request.endpoint and request.endpoint not in rotas_livres:
        # Verifica se a chave de acesso única da aba existe
        if not session.get("token_sessao_ativa"):
            return redirect(url_for("login"))


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0, post-check=0, pre-check=0"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response


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
    conn.commit()
    conn.close()


init_spare_parts_db()

# Registro dos Blueprints
app.register_blueprint(portaria_bp)
app.register_blueprint(conferencia_bp)
app.register_blueprint(compras_bp)
app.register_blueprint(arquivo_bp)


# ============================================================
# Sistema de Autenticação Estrito
# ============================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    # Sempre que entra na tela de login, limpa qualquer vestígio anterior
    session.clear()

    if request.method == "POST":
        senha_digitada = request.form.get("senha")
        if senha_digitada == "1234":
            # Cria um identificador único de sessão para esta aba/instância
            import uuid

            session["token_sessao_ativa"] = str(uuid.uuid4())
            return redirect(url_for("index"))
        else:
            flash(
                "Senha incorreta! Para este protótipo, utilize a senha: 1234",
                "danger",
            )

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/api/pecas-criticas", methods=["GET"])
def listar_pecas_criticas():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pecas_criticas")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
