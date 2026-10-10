import sqlite3
from datetime import datetime
from flask import Blueprint, jsonify, request, Response

compras_bp = Blueprint("compras", __name__)


def garantir_tabelas_compras():
    conn = sqlite3.connect("cd_virtual.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordens_compra_insumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_po TEXT UNIQUE,
            nome_insumo TEXT,
            fornecedor TEXT,
            quantidade INTEGER,
            categoria TEXT,
            data_emissao TEXT,
            status TEXT DEFAULT 'PO_EMITIDA_AGUARDANDO_RECEBIMENTO'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fornecedores_hub (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            strikes INTEGER DEFAULT 0,
            status TEXT DEFAULT 'HOMOLOGADO',
            otif_score REAL DEFAULT 100.0
        )
    """)

    colunas_existentes = [
        row[1]
        for row in cursor.execute("PRAGMA table_info(ordens_compra_insumos)").fetchall()
    ]
    if "categoria" not in colunas_existentes:
        cursor.execute("ALTER TABLE ordens_compra_insumos ADD COLUMN categoria TEXT")
    if "data_emissao" not in colunas_existentes:
        cursor.execute("ALTER TABLE ordens_compra_insumos ADD COLUMN data_emissao TEXT")

    conn.commit()
    conn.close()


garantir_tabelas_compras()


@compras_bp.route("/api/compras/insumos/<categoria>", methods=["GET"])
def buscar_insumos_categoria(categoria):
    insumos_hub = {
        "carga_seca": [
            {
                "id": 101,
                "nome_insumo": "Paletes PBR Madeira (Selo FSC)",
                "fornecedor": "Madeira Castro",
                "saldo": 120,
                "demanda": 300,
                "unidade": "un",
            },
            {
                "id": 102,
                "nome_insumo": "Filme Stretch Padrão 500mm",
                "fornecedor": "Embalagens Paraná",
                "saldo": 15,
                "demanda": 50,
                "unidade": "bob",
            },
            {
                "id": 103,
                "nome_insumo": "Fita de Arquear PP",
                "fornecedor": "Suprimentos Sul",
                "saldo": 5,
                "demanda": 20,
                "unidade": "rolo",
            },
        ],
        "molhados_quimicos": [
            {
                "id": 201,
                "nome_insumo": "Kit Contenção FISPQ",
                "fornecedor": "Química Proteção",
                "saldo": 10,
                "demanda": 8,
                "unidade": "kit",
            },
            {
                "id": 202,
                "nome_insumo": "Cantoneiras Papelão Reforçado",
                "fornecedor": "Embalagens Paraná",
                "saldo": 200,
                "demanda": 500,
                "unidade": "un",
            },
            {
                "id": 203,
                "nome_insumo": "Tambores Reter Pingos",
                "fornecedor": "Suprimentos Sul",
                "saldo": 4,
                "demanda": 10,
                "unidade": "un",
            },
        ],
        "pereciveis": [
            {
                "id": 301,
                "nome_insumo": "Paletes Plásticos Higienizáveis",
                "fornecedor": "PlástiCastro",
                "saldo": 40,
                "demanda": 150,
                "unidade": "un",
            },
            {
                "id": 302,
                "nome_insumo": "Filme Stretch Térmico (Câmara Fria)",
                "fornecedor": "Embalagens Paraná",
                "saldo": 8,
                "demanda": 30,
                "unidade": "bob",
            },
            {
                "id": 303,
                "nome_insumo": "Etiquetas Térmicas Umidade",
                "fornecedor": "Automação Castro",
                "saldo": 500,
                "demanda": 2000,
                "unidade": "etq",
            },
        ],
        "apoio_infra": [
            {
                "id": 401,
                "nome_insumo": "Ribbon Impressão Térmica",
                "fornecedor": "Automação Castro",
                "saldo": 6,
                "demanda": 15,
                "unidade": "un",
            },
            {
                "id": 402,
                "nome_insumo": "Resmas Papel A4 Fiscal",
                "fornecedor": "Papelaria Central",
                "saldo": 12,
                "demanda": 50,
                "unidade": "pct",
            },
            {
                "id": 403,
                "nome_insumo": "Lacres Numerados Baú",
                "fornecedor": "Suprimentos Sul",
                "saldo": 100,
                "demanda": 500,
                "unidade": "un",
            },
        ],
    }
    return jsonify({"categoria": categoria, "insumos": insumos_hub.get(categoria, [])})


@compras_bp.route("/api/compras/emitir-po", methods=["POST"])
def emitir_po_insumo():
    dados = request.json
    codigo_po = f"PO-INSUMO-{dados.get('insumo_id')}-2026"
    data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M")

    conn = sqlite3.connect("cd_virtual.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO ordens_compra_insumos
        (codigo_po, nome_insumo, fornecedor, quantidade, categoria, data_emissao)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            codigo_po,
            dados.get("nome_insumo"),
            dados.get("fornecedor"),
            dados.get("quantidade"),
            dados.get("categoria", "nao_informada"),
            data_emissao,
        ),
    )
    conn.commit()
    conn.close()

    return jsonify(
        {"status": "sucesso", "codigo_po": codigo_po, "data_emissao": data_emissao}
    )


@compras_bp.route("/api/kpi/detalhes-otif", methods=["GET"])
def detalhar_kpi_otif():
    conn = sqlite3.connect("cd_virtual.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM fornecedores_hub ORDER BY strikes DESC, otif_score ASC"
    )
    fornecedores = cursor.fetchall()
    conn.close()

    if not fornecedores:
        dados_demo = [
            {
                "nome": "Madeira Castro",
                "categoria": "Carga Seca",
                "otif_score": 98.5,
                "strikes": 0,
                "status": "HOMOLOGADO",
            },
            {
                "nome": "Embalagens Paraná",
                "categoria": "Embalagens",
                "otif_score": 92.0,
                "strikes": 1,
                "status": "EM_ALERTA",
            },
            {
                "nome": "Química Proteção",
                "categoria": "Molhados/Químicos",
                "otif_score": 88.0,
                "strikes": 2,
                "status": "RISCO_CRITICO",
            },
            {
                "nome": "Suprimentos Sul",
                "categoria": "Apoio",
                "otif_score": 65.0,
                "strikes": 3,
                "status": "BANIDO_OTIF",
            },
        ]
        return jsonify(dados_demo)

    return jsonify([dict(f) for f in fornecedores])


@compras_bp.route("/api/kpi/fornecedor-detalhes/<nome_fornecedor>", methods=["GET"])
def detalhar_historico_fornecedor(nome_fornecedor):
    conn = sqlite3.connect("cd_virtual.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM fornecedores_hub WHERE nome = ?", (nome_fornecedor,))
    fornecedor = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM ordens_compra_insumos WHERE fornecedor = ? ORDER BY id DESC",
        (nome_fornecedor,),
    )
    pos = cursor.fetchall()
    conn.close()

    return jsonify(
        {
            "fornecedor": (
                dict(fornecedor)
                if fornecedor
                else {
                    "nome": nome_fornecedor,
                    "strikes": 0,
                    "status": "HOMOLOGADO",
                    "categoria": "Geral",
                }
            ),
            "historico_pos": [dict(po) for po in pos],
        }
    )


@compras_bp.route("/api/kpi/exportar-fornecedor-csv/<nome_fornecedor>", methods=["GET"])
def exportar_fornecedor_csv(nome_fornecedor):
    conn = sqlite3.connect("cd_virtual.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM ordens_compra_insumos WHERE fornecedor = ? ORDER BY id DESC",
        (nome_fornecedor,),
    )
    pos = cursor.fetchall()
    conn.close()

    csv = f"RELATORIO DE AUDITORIA - FORNECEDOR: {nome_fornecedor}\n"
    csv += "Codigo_PO;Data_Emissao;Categoria;Insumo;Quantidade;Status\n"
    if pos:
        for p in pos:
            csv += f"{p['codigo_po']};{p['data_emissao'] or ''};{p['categoria'] or ''};{p['nome_insumo']};{p['quantidade']};{p['status']}\n"
    else:
        csv += "Nenhuma PO registrada para este fornecedor.\n"

    filename = f"auditoria_{nome_fornecedor.lower().replace(' ', '_')}.csv"
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@compras_bp.route("/api/kpi/detalhes-giro/<periodo>", methods=["GET"])
def detalhar_kpi_giro_por_periodo(periodo):
    dados_periodo = {
        "diario": [
            {
                "insumo": "Filme Stretch Padrão (Lote 01)",
                "posicao": "DOCA-02",
                "dias_imobilizado": 2,
                "qtd": 15,
                "status": "🟢 Giro Rápido (Diário)",
            },
            {
                "insumo": "Resmas Papel A4 Fiscal",
                "posicao": "ESCRITÓRIO",
                "dias_imobilizado": 1,
                "qtd": 12,
                "status": "🟢 Giro Diário",
            },
        ],
        "semanal": [
            {
                "insumo": "Paletes PBR Madeira (Lote 104)",
                "posicao": "RUA-A-01",
                "dias_imobilizado": 14,
                "qtd": 80,
                "status": "🟡 Atenção Semanal",
            },
            {
                "insumo": "Fita de Arquear PP 19mm",
                "posicao": "DOCA-APOIO",
                "dias_imobilizado": 10,
                "qtd": 15,
                "status": "🟢 Normal Semanal",
            },
        ],
        "trimestral": [
            {
                "insumo": "Paletes PBR Madeira (Lote 104)",
                "posicao": "RUA-A-01",
                "dias_imobilizado": 75,
                "qtd": 80,
                "status": "🔴 Capital Parado (>30d)",
            },
            {
                "insumo": "Tambores Reter Pingos",
                "posicao": "RUA-C-04",
                "dias_imobilizado": 65,
                "qtd": 4,
                "status": "🔴 Baixo Giro Trimestral",
            },
        ],
        "anual": [
            {
                "insumo": "Paletes PBR Madeira (Encalhado Anual)",
                "posicao": "PULMÃO-Z",
                "dias_imobilizado": 210,
                "qtd": 120,
                "status": "🔴 Obsolescência / Inativo",
            }
        ],
    }
    return jsonify(
        {
            "periodo": periodo,
            "itens": dados_periodo.get(periodo, dados_periodo["semanal"]),
        }
    )


@compras_bp.route("/api/kpi/exportar-giro-csv/<periodo>", methods=["GET"])
def exportar_giro_periodo_csv(periodo):
    dados = {
        "diario": [
            ("Filme Stretch Padrão", "DOCA-02", 2, 15, "Giro Rapido"),
            ("Resmas Papel A4", "ESCRITORIO", 1, 12, "Giro Diario"),
        ],
        "semanal": [
            ("Paletes PBR Madeira", "RUA-A-01", 14, 80, "Atencao Semanal"),
            ("Fita Arquear PP", "DOCA-APOIO", 10, 15, "Normal Semanal"),
        ],
        "trimestral": [
            ("Paletes PBR Madeira", "RUA-A-01", 75, 80, "Capital Parado"),
            ("Tambores Reter Pingos", "RUA-C-04", 65, 4, "Baixo Giro Trimestral"),
        ],
        "anual": [
            (
                "Paletes PBR Madeira (Inativo)",
                "PULMAO-Z",
                210,
                120,
                "Obsolescência Anual",
            )
        ],
    }.get(periodo, [])

    csv = f"RELATORIO DE GIRO DE ESTOQUE - PERIODO: {periodo.upper()}\nInsumo;Posicao_WMS;Dias_Imobilizado;Quantidade;Status\n"
    for d in dados:
        csv += f"{d[0]};{d[1]};{d[2]};{d[3]};{d[4]}\n"

    return Response(
        csv,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=relatorio_giro_{periodo}.csv"
        },
    )


@compras_bp.route("/api/kpi/detalhes-acuracia", methods=["GET"])
def detalhar_kpi_acuracia_real():
    conn = sqlite3.connect("cd_virtual.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ordens_compra_insumos ORDER BY id DESC LIMIT 10")
    pos = cursor.fetchall()
    conn.close()

    divergencias = [
        {
            "data": "10/10/2026 14:20",
            "po": "PO-INSUMO-101-2026",
            "insumo": "Paletes PBR Madeira",
            "esperado_contado": "300 vs 295",
            "motivo": "⚠️ Divergência de 5 un na Doca (Retido)",
        }
    ]
    for p in pos:
        divergencias.append(
            {
                "data": p["data_emissao"] or "10/10/2026",
                "po": p["codigo_po"],
                "insumo": p["nome_insumo"],
                "esperado_contado": f"{p['quantidade']} vs {p['quantidade']}",
                "motivo": "Conferência Cega OK",
            }
        )
    return jsonify(divergencias)


@compras_bp.route("/api/kpi/exportar-acuracia-csv", methods=["GET"])
def exportar_acuracia_csv():
    csv = "Data;Codigo_PO;Insumo;Esperado_vs_Contado;Ocorrencia\n"
    csv += "10/10/2026 14:20;PO-INSUMO-101-2026;Paletes PBR Madeira;300 vs 295;Divergencia de 5 un na Doca\n"
    return Response(
        csv,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=relatorio_acuracia_inventario.csv"
        },
    )


@compras_bp.route("/api/compras/historico", methods=["GET"])
def listar_historico_pos():
    conn = sqlite3.connect("cd_virtual.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ordens_compra_insumos ORDER BY id DESC")
    linhas = cursor.fetchall()
    conn.close()
    return jsonify([dict(l) for l in linhas])


@compras_bp.route("/api/compras/download/<codigo_po>", methods=["GET"])
def baixar_po(codigo_po):
    conn = sqlite3.connect("cd_virtual.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM ordens_compra_insumos WHERE codigo_po = ?", (codigo_po,)
    )
    linha = cursor.fetchone()
    conn.close()
    if not linha:
        return jsonify({"erro": "PO não encontrada"}), 404
    conteudo = f"ORDEM DE COMPRA: {linha['codigo_po']}\nInsumo: {linha['nome_insumo']}\nFornecedor: {linha['fornecedor']}\nQtd: {linha['quantidade']}\nSelo ESG: FSC Madeira Certificada"
    return Response(
        conteudo,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename={codigo_po}.txt"},
    )


@compras_bp.route("/api/compras/copiar/<codigo_po>", methods=["GET"])
def copiar_po_email(codigo_po):
    conn = sqlite3.connect("cd_virtual.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM ordens_compra_insumos WHERE codigo_po = ?", (codigo_po,)
    )
    linha = cursor.fetchone()
    conn.close()
    if not linha:
        return jsonify({"erro": "PO não encontrada"}), 404
    texto = f"Prezado {linha['fornecedor']}, segue PO {linha['codigo_po']} para o insumo {linha['nome_insumo']} ({linha['quantidade']} un)."
    return jsonify({"texto": texto})
