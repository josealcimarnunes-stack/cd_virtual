from flask import Blueprint, jsonify, request

portaria_bp = Blueprint("portaria", __name__)


@portaria_bp.route("/api/portaria/processar-completo", methods=["POST"])
def processar_portaria_completa():
    dados = request.get_json() or {}

    # 1. Identificação
    placa = dados.get("placa")
    motorista = dados.get("motorista")

    # 2. Balança
    peso_bruto = dados.get("peso_bruto", 0)

    # 3. Checklist
    chk_lacre = dados.get("chk_lacre", False)
    chk_bau = dados.get("chk_bau", False)
    chk_epis = dados.get("chk_epis", False)

    # Validação de Segurança
    if not (chk_lacre and chk_bau and chk_epis):
        return (
            jsonify(
                {
                    "status": "recusado",
                    "mensagem": f"🚫 ENTRADA BLOQUEADA para {placa}! Reprovado no checklist de inspeção e segurança.",
                    "cor_luz": "VERMELHO",
                }
            ),
            400,
        )

    # 4. Atribuição de Doca e Resposta
    doca = dados.get("doca_destino", "DOCA-01")
    pager = dados.get("pager", "PAGER-01")

    return jsonify(
        {
            "status": "sucesso",
            "mensagem": f"✅ VEÍCULO LIBERADO!\n\nPlaca: {placa}\nMotorista: {motorista}\nPeso Entrada: {peso_bruto} Kg\nDestino: {doca} | Pager: {pager}",
            "proxima_etapa": "conferencia_doca",
            "doca": doca,
            "cor_luz": "VERDE",
        }
    )
