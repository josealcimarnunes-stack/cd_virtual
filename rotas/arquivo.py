from datetime import datetime
import sqlite3
from flask import Blueprint, flash, redirect, render_template, request, url_for

arquivo_bp = Blueprint("arquivo", __name__)
DB_PATH = "cd_virtual.db"


def init_arquivo_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cautelas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_documento TEXT NOT NULL,
            identificacao TEXT NOT NULL,
            solicitante TEXT NOT NULL,
            data_retirada TEXT NOT NULL,
            previsao_devolucao TEXT NOT NULL,
            data_devolucao_real TEXT,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# Garante que a tabela existe no banco ao carregar a rota
init_arquivo_db()


@arquivo_bp.route("/arquivo", methods=["GET", "POST"])
def listar_cautelas():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":
        tipo_documento = request.form.get("tipo_documento")
        identificacao = request.form.get("identificacao")
        solicitante = request.form.get("solicitante")
        previsao_devolucao = request.form.get("previsao_devolucao")
        data_retirada = datetime.now().strftime("%Y-%m-%d %H:%M")

        cursor.execute(
            """
            INSERT INTO cautelas (tipo_documento, identificacao, solicitante, data_retirada, previsao_devolucao, status)
            VALUES (?, ?, ?, ?, ?, 'Retirado')
        """,
            (
                tipo_documento,
                identificacao,
                solicitante,
                data_retirada,
                previsao_devolucao,
            ),
        )
        conn.commit()
        flash("Retirada física de documento registrada com sucesso!", "success")
        conn.close()
        return redirect(url_for("arquivo.listar_cautelas"))

    cursor.execute("SELECT * FROM cautelas ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    data_hoje = datetime.now().strftime("%Y-%m-%d")
    cautelas = []

    for row in rows:
        c = dict(row)
        # Regra de Alerta Dinâmico: se a previsão é menor que hoje e não devolveu, marca como atrasado
        c["esta_atrasado"] = (
            c["status"] == "Retirado" and c["previsao_devolucao"] < data_hoje
        )
        cautelas.append(c)

    return render_template("arquivo.html", cautelas=cautelas)


@arquivo_bp.route("/arquivo/devolver/<int:cautela_id>", methods=["POST"])
def devolver_cautela(cautela_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    data_hoje_hora = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute(
        """
        UPDATE cautelas 
        SET status = 'Devolvido', data_devolucao_real = ? 
        WHERE id = ?
    """,
        (data_hoje_hora, cautela_id),
    )

    conn.commit()
    conn.close()
    flash("Baixa de cautela concluída e documento devolvido ao arquivo!", "info")
    return redirect(url_for("arquivo.listar_cautelas"))
