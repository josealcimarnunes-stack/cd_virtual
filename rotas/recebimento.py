from flask import Blueprint, jsonify, request

recebimento_bp = Blueprint("recebimento", __name__)


@recebimento_bp.route("/api/recebimento/conferir", methods=["POST"])
def conferir_carga():
    data = request.get_json() or {}
    qtd_contada = data.get("quantidade", 100)

    # Exemplo de regra: se a contagem for menor que 100, sinaliza divergência
    if qtd_contada < 100:
        return jsonify(
            {
                "status": "alerta",
                "mensagem": f"Divergência! Esperado 100, recebido {qtd_contada}. Requer laudo de avaria.",
                "cor_luz": "VERMELHO",
            }
        )

    return jsonify(
        {
            "status": "sucesso",
            "mensagem": "Conferência concluída com 100% de acuracidade. Liberado para endereçamento!",
            "cor_luz": "VERDE",
        }
    )
