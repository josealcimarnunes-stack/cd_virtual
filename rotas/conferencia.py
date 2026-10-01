from flask import Blueprint, request, jsonify

# 1. Definição do Blueprint da Conferência / Doca
conferencia_bp = Blueprint("conferencia", __name__)


# 2. Rota para processar e finalizar o recebimento na Doca
@conferencia_bp.route("/api/conferencia/finalizar", methods=["POST"])
def finalizar_conferencia():
    dados = request.get_json() or {}

    doca = dados.get("doca", "01")
    calco = dados.get("calco_ok")
    nivelador = dados.get("nivelador_ok")
    qtd_avaria = dados.get("qtd_avaria", 0)
    tipo_avaria = dados.get("tipo_avaria", "")
    obs_avaria = dados.get("obs_avaria", "")

    # Validação dos itens de segurança da doca
    if not calco or calco == "nao":
        return (
            jsonify(
                {
                    "status": "erro",
                    "mensagem": "🛑 SEGURANÇA TRAVADA: O calço de roda precisa estar aplicado antes de descarregar!",
                }
            ),
            400,
        )

    # Lógica de sucesso no recebimento
    msg = f"✅ Recebimento da Doca {doca} finalizado com sucesso! Carga liberada para Putaway no WMS."
    if int(qtd_avaria) > 0:
        msg += f" ⚠️ Registrado {qtd_avaria} vol. com avaria ({tipo_avaria}) retidos na área de quarentena."

    return jsonify({"status": "sucesso", "mensagem": msg, "doca": doca})
