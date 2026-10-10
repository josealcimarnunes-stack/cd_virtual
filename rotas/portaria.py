import random
import sqlite3
from flask import Blueprint, Response, jsonify, request

portaria_bp = Blueprint("portaria", __name__)


def conectar_banco():
    return sqlite3.connect("cd_virtual.db")


@portaria_bp.route("/api/portaria/processar-completo", methods=["POST"])
def processar_portaria_completa():
    dados = request.get_json() or {}

    # Dados informados na tela da Guarita pelo operador
    placa_informada = dados.get("placa", "").strip().upper()
    carreta_informada = dados.get("carreta", "").strip().upper()
    motorista_informado = dados.get("motorista", "").strip()
    doc_informado = dados.get("doc_motorista", "").strip()
    po_informado = dados.get("po", "").strip().upper()

    # Chaves Fiscais informadas (DANFE, CT-e, MDF-e)
    chave_danfe = dados.get("chave_danfe", "").strip()
    chave_cte = dados.get("chave_cte", "").strip()
    chave_mdfe = dados.get("chave_mdfe", "").strip()

    # Status físicos da portaria
    chk_lacre = dados.get("chk_lacre", True)
    chk_epis = dados.get("chk_epis", True)
    chk_bau = dados.get("chk_bau", True)

    if not placa_informada:
        return (
            jsonify(
                {
                    "status": "recusado",
                    "mensagem": (
                        "Informe a placa do cavalo para iniciar o cruzamento de"
                        " dados da portaria."
                    ),
                }
            ),
            400,
        )

    conn = conectar_banco()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Busca o agendamento oficial no ERP (SQLite)
    cursor.execute(
        """
        SELECT * FROM cenarios_portaria 
        WHERE UPPER(placa) = ?
    """,
        (placa_informada,),
    )
    cenario_real = cursor.fetchone()
    conn.close()

    # 1. Se a placa não consta no sistema (Caminhão não agendado)
    if not cenario_real:
        return (
            jsonify(
                {
                    "status": "bloqueio_diagnostico",
                    "mensagem": (
                        f"⚠️ ALERTA DO WMS: A placa do cavalo '{placa_informada}'"
                        " não possui agendamento prévio no ERP!"
                    ),
                    "falha_real": "placa",
                    "cor_luz": "VERMELHO",
                }
            ),
            400,
        )

    # 2. Validação rigorosa da Placa da Carreta
    if (
        carreta_informada
        and carreta_informada != str(cenario_real["carreta"]).strip().upper()
    ):
        return (
            jsonify(
                {
                    "status": "bloqueio_diagnostico",
                    "mensagem": (
                        f"⚠ DIVERGÊNCIA DE FROTA: A carreta informada"
                        f" ('{carreta_informada}') não confere com a agendada"
                        f" ('{cenario_real['carreta']}')."
                    ),
                    "falha_real": "placa",
                    "cor_luz": "VERMELHO",
                }
            ),
            400,
        )

    # 3. Validação rigorosa do Motorista e Documento (CPF/CNH)
    if (
        motorista_informado
        and motorista_informado.lower()
        != str(cenario_real["motorista"]).strip().lower()
    ):
        return (
            jsonify(
                {
                    "status": "bloqueio_diagnostico",
                    "mensagem": (
                        f"⚠️ DIVERGÊNCIA DE PESSOAL: O motorista presente"
                        f" ('{motorista_informado}') difere do credenciado"
                        f" ('{cenario_real['motorista']}')."
                    ),
                    "falha_real": "documento",
                    "cor_luz": "VERMELHO",
                }
            ),
            400,
        )

    if doc_informado and doc_informado != str(cenario_real["doc_motorista"]).strip():
        return (
            jsonify(
                {
                    "status": "bloqueio_diagnostico",
                    "mensagem": (
                        "⚠️ FALHA DOCUMENTAL: O documento do motorista não confere"
                        " com a base do ERP."
                    ),
                    "falha_real": "documento",
                    "cor_luz": "VERMELHO",
                }
            ),
            400,
        )

    # 4. Validação do Pedido (PO / Ordem de Compra)
    if po_informado and po_informado != str(cenario_real["po"]).strip().upper():
        return (
            jsonify(
                {
                    "status": "bloqueio_diagnostico",
                    "mensagem": (
                        f"⚠️ DIVERGÊNCIA COMERCIAL: O PO informado"
                        f" ('{po_informado}') não bate com a ordem de compra"
                        " esperada."
                    ),
                    "falha_real": "fiscal",
                    "cor_luz": "VERMELHO",
                }
            ),
            400,
        )

    # 5. Validações físicas de Segurança (EPIs, Baú e Lacre)
    if not chk_epis:
        return (
            jsonify(
                {
                    "status": "bloqueio_diagnostico",
                    "mensagem": (
                        "⚠️ ACESSO NEGADO: Motorista sem o kit completo de EPIs"
                        " obrigatórios."
                    ),
                    "falha_real": "inspecao",
                    "cor_luz": "VERMELHO",
                }
            ),
            400,
        )

    if not chk_bau:
        return (
            jsonify(
                {
                    "status": "bloqueio_diagnostico",
                    "mensagem": (
                        "⚠️ RETENÇÃO: Condições físicas do baú reprovadas na"
                        " inspeção visual."
                    ),
                    "falha_real": "inspecao",
                    "cor_luz": "VERMELHO",
                }
            ),
            400,
        )

    if not chk_lacre or cenario_real["tipo_falha_esperada"] == "inspecao":
        return (
            jsonify(
                {
                    "status": "bloqueio_diagnostico",
                    "mensagem": (
                        f"⚠️ RETENÇÃO DE SEGURANÇA:"
                        f" {cenario_real['descricao_problema']}"
                    ),
                    "falha_real": "inspecao",
                    "cor_luz": "VERMELHO",
                }
            ),
            400,
        )

    # 6. Verificação geral de falha cadastrada no cenário do banco
    if cenario_real["tipo_falha_esperada"] != "ok":
        return (
            jsonify(
                {
                    "status": "bloqueio_diagnostico",
                    "mensagem": (
                        f"⚠ BLOQUEIO DO SISTEMA:"
                        f" {cenario_real['descricao_problema']}"
                    ),
                    "falha_real": cenario_real["tipo_falha_esperada"],
                    "cor_luz": "VERMELHO",
                }
            ),
            400,
        )

    # 7. Sucesso absoluto (Tudo bateu perfeitamente com o ERP)
    return jsonify(
        {
            "status": "sucesso",
            "mensagem": (
                f"✅ CRUZAMENTO CONCLUÍDO COM SUCESSO!\nPlaca:"
                f" {cenario_real['placa']}\nMotorista:"
                f" {cenario_real['motorista']}\nPO: {cenario_real['po']}\nDirecionado"
                " para: Balança e Doca-02"
            ),
            "proxima_etapa": "balanca",
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
                    "🎉 Parabéns! Auditoria realizada com sucesso. Você"
                    " identificou exatamente a divergência fiscal/operacional"
                    " detectada pelo WMS."
                ),
            }
        )
    else:
        return jsonify(
            {
                "acertou": False,
                "mensagem": (
                    "❌ Diagnóstico incorreto! Analise detalhadamente os dados"
                    " cruzados do ERP para encontrar a falha real."
                ),
            }
        )


# Rota nova adicionada para o gerador de exercícios embaralhados para download
@portaria_bp.route("/api/portaria/baixar-exercicios-personalizado", methods=["GET"])
def baixar_exercicios_personalizado():
    try:
        quantidade = int(request.args.get("qtd", 10))
    except ValueError:
        quantidade = 10

    conn = conectar_banco()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cenarios_portaria")
    registros = cursor.fetchall()
    conn.close()

    if not registros:
        return Response(
            "Nenhum cenário cadastrado no banco.", mimetype="text/plain; charset=utf-8"
        )

    lista_registros = [dict(reg) for reg in registros]
    random.shuffle(lista_registros)
    lista_selecionada = lista_registros[:quantidade]

    linhas = []
    linhas.append("=" * 80)
    linhas.append(" 📋 FOLHA DE EXERCÍCIOS / PROVA PRÁTICA - PORTARIA WMS")
    linhas.append(
        f" Total de Cargas para Auditoria: {len(lista_selecionada)} (Embaralhadas)"
    )
    linhas.append(
        " Instruções: Insira os dados abaixo no sistema WMS para validar a entrada."
    )
    linhas.append("=" * 80 + "\n")

    for idx, reg in enumerate(lista_selecionada, start=1):
        # REMOVIDO O GABARITO EXPLÍCITO DO TÍTULO! Agora o aluno descobre testando no sistema.
        linhas.append(f"EXERCÍCIO {idx:02d}")
        linhas.append(f"  • Placa (Cavalo): {reg['placa']} | Carreta: {reg['carreta']}")
        linhas.append(
            f"  • Motorista: {reg['motorista']} (CPF/Doc: {reg['doc_motorista']})"
        )
        linhas.append(f"  • Pedido (PO): {reg['po']}")
        linhas.append(f"  • Chave MDF-e: {reg['chave_mdfe']}")
        linhas.append(
            f"  • Observação do Porteiro / Guarita: {reg['descricao_problema']}"
        )
        linhas.append("-" * 80)

    conteudo = "\n".join(linhas)

    return Response(
        conteudo,
        mimetype="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=prova_pratica_portaria_{quantidade}_itens.txt"
        },
    )
