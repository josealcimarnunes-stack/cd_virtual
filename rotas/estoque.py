from flask import Blueprint, jsonify

estoque_bp = Blueprint("estoque", __name__)


@estoque_bp.route("/api/estoque/status", methods=["GET"])
def status_estoque():
    return jsonify(
        {"capacidade_total": 500, "ocupacao_atual": 120, "posicoes_livres": 380}
    )
