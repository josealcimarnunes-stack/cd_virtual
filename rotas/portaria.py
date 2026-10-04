import sqlite3
from flask import Blueprint, jsonify, request

portaria_bp = Blueprint("portaria", __name__)


def conectar_banco():
    return sqlite3.connect("cd_virtual.db")


@portaria_bp.route("/api/portaria/processar-completo", methods=["POST"])
def processar_portaria_completa():
    dados = request.get_json() or {}
    placa_informada = dados.get("placa", "").strip().upper()  # O que o operador digitou
    po_informado = dados.get("po", "").strip().upper()  # Pedido informado no papel

    if not placa_informada and not po_informado:
        return (
            jsonify(
                {
                    "status": "recusado",
                    "mensagem": (
                        "Informe a placa ou o número do pedido (PO) da nota física."
                    ),
                }
            ),
            400,
        )

    conn = conectar_banco()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # O sistema cruza os dados digitados com o banco de dados oficial
    cursor.execute(
        """
        SELECT * FROM cenarios_portaria 
        WHERE UPPER(placa) = ? OR UPPER(po) = ?
    """,
        (placa_informada, po_informado),
    )
    cenario_real = cursor.fetchone()
    conn.close()

    # Se o sistema não encontrar a placa/PO no banco (Caminhão Fantasma ou Nota Fake externa)
    if not cenario_real:
        return (
            jsonify(
                {
                    "status": "bloqueio_diagnostico",
                    "mensagem": (
                        f"⚠️ ALERTA DO SISTEMA: A placa '{placa_informada}' ou PO"
                        " informada não consta nos registros oficiais do ERP / Pedidos"
                        " de Compra!"
                    ),
                    "falha_real": "fiscal",  # Trata como divergência fiscal/nota fake
                    "cor_luz": "VERMELHO",
                }
            ),
            400,
        )

    falha_esperada = cenario_real["tipo_falha_esperada"]

    # Se o banco detectou que há uma irregularidade cadastrada para este veículo
    if falha_esperada != "ok":
        return (
            jsonify(
                {
                    "status": "bloqueio_diagnostico",
                    "mensagem": (
                        f"⚠️ BLOQUEIO AUTOMÁTICO DO WMS! O cruzamento dos dados para a"
                        f" placa {cenario_real['placa']} indicou uma divergência de"
                        " conformidade. Qual é o diagnóstico correto?"
                    ),
                    "falha_real": falha_esperada,
                    "cor_luz": "VERMELHO",
                }
            ),
            400,
        )

    # Tudo OK - Cruzamento validado com sucesso pelo ERP/WMS
    return jsonify(
        {
            "status": "sucesso",
            "mensagem": (
                f"✅ ENTRADA VALIDADA COM SUCESSO!\nPlaca: {cenario_real['placa']}\nPO:"
                f" {cenario_real['po']}\nDirecionado para: DOCA-02"
            ),
            "proxima_etapa": "conferencia_doca",
            "cor_luz": "VERDE",
            "doca": "DOCA-02",
        }
    )


@portaria_bp.route("/api/portaria/validar-diagnostico", methods=["POST"])
def validar_diagnostico():
    dados = request.get_json() or {}
    falha_real = dados.get("falha_real")
    resposta_escolhida = dados.get("resposta_escolhida")

    if resposta_escolhida == falha_real:
        return jsonify(
            {
                "acertou": True,
                "mensagem": (
                    "🎉 Parabéns! Auditoria realizada com sucesso. Você identificou"
                    " corretamente a falha que o sistema detectou."
                ),
            }
        )
    else:
        return jsonify(
            {
                "acertou": False,
                "mensagem": (
                    "❌ Diagnóstico incorreto! A divergência real detectada no sistema"
                    " é outra. Releia os dados da nota."
                ),
            }
        )
