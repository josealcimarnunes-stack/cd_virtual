import sqlite3


def gerar_ambiente_treinamento():
    conexao = sqlite3.connect("cd_virtual.db")
    cursor = conexao.cursor()

    # 1. Recria a tabela limpa
    cursor.execute("DROP TABLE IF EXISTS cenarios_portaria")
    cursor.execute("""
        CREATE TABLE cenarios_portaria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL,
            carreta TEXT NOT NULL,
            motorista TEXT NOT NULL,
            doc_motorista TEXT NOT NULL,
            po TEXT NOT NULL,
            chave_danfe TEXT,
            chave_cte TEXT,
            chave_mdfe TEXT,
            tipo_falha_esperada TEXT NOT NULL,
            descricao_problema TEXT NOT NULL
        )
    """)

    cenarios = []
    conteudo_impresso = []

    conteudo_impresso.append("=" * 80)
    conteudo_impresso.append(
        " 📋 FOLHA DE EXERCÍCIOS E SIMULAÇÃO - PORTARIA WMS (TREINAMENTO)"
    )
    conteudo_impresso.append(
        " Instruções para o Aluno: Utilize os dados abaixo para realizar a" " triagem"
    )
    conteudo_impresso.append(
        " de entrada na Guarita. Fique atento às pendências fiscais!"
    )
    conteudo_impresso.append("=" * 80 + "\n")

    conteudo_impresso.append(
        "--- BLOCO 1: CARGAS REGULARES (Devem passar direto) ---\n"
    )

    # 2. Gerar 25 Cargas Regulares
    for i in range(1, 26):
        placa = f"TRK-{i:04d}"
        carreta = f"CRT-{i:04d}"
        motorista = f"Motorista Regular {i}"
        doc = f"123.456.78{i:02d}-00"
        po = f"PO-2026-{9000 + i}"
        danfe = f"35260812345678000195550010000{i:05d}1234567"
        cte = f"35260898765432000195570010000{i:05d}9876543"
        mdfe = f"35260845678912000195580010000{i:05d}5544332"

        cenarios.append(
            (
                placa,
                carreta,
                motorista,
                doc,
                po,
                danfe,
                cte,
                mdfe,
                "ok",
                "Carga 100% regular.",
            )
        )

        conteudo_impresso.append(
            f"Exercício {i:02d} | Placa: {placa} | Carreta: {carreta} | Motorista:"
            f" {motorista} (CPF: {doc})"
        )
        conteudo_impresso.append(f"          | Pedido (PO): {po} | Chave MDF-e: {mdfe}")
        conteudo_impresso.append("-" * 80)

    conteudo_impresso.append(
        "\n--- BLOCO 2: CARGAS COM PENDÊNCIA (Devem disparar o Quiz Fiscal) ---\n"
    )

    # 3. Gerar 5 Cargas com Falha Fiscal (MDF-e em aberto)
    for j in range(1, 6):
        placa = f"ERR-MDF-{j:02d}"
        carreta = f"CRT-ERR-{j:02d}"
        motorista = f"Motorista Com Pendencia {j}"
        doc = f"999.888.77{j:02d}-99"
        po = f"PO-2026-88{j:02d}"
        danfe = f"35260899999999000195550010000{j:05d}1111111"
        cte = f"35260899999999000195570010000{j:05d}2222222"
        mdfe = "PENDENTE-SEFAZ"  # O gatilho do erro

        cenarios.append(
            (
                placa,
                carreta,
                motorista,
                doc,
                po,
                danfe,
                cte,
                mdfe,
                "fiscal",
                "MDF-e em aberto na SEFAZ.",
            )
        )

        conteudo_impresso.append(
            f"ALERTA EXERCÍCIO {25+j:02d} | Placa: {placa} | Carreta: {carreta} |"
            f" Motorista: {motorista} (CPF: {doc})"
        )
        conteudo_impresso.append(
            f"                 | Pedido (PO): {po} | Chave MDF-e: {mdfe}"
        )
        conteudo_impresso.append(
            "                 -> ATENÇÃO: Esta carga possui pendência fiscal na"
            " SEFAZ!"
        )
        conteudo_impresso.append("-" * 80)

    # Salva no Banco de Dados SQLite
    cursor.executemany(
        """
        INSERT INTO cenarios_portaria (
            placa, carreta, motorista, doc_motorista, po, 
            chave_danfe, chave_cte, chave_mdfe, tipo_falha_esperada, descricao_problema
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        cenarios,
    )

    conexao.commit()
    conexao.close()

    # Salva o arquivo de texto para impressão
    with open("folha_exercicios_alunos.txt", "w", encoding="utf-8") as arquivo_txt:
        arquivo_txt.write("\n".join(conteudo_impresso))

    print(
        "✅ Sucesso absoluto! Banco populado com 30 cargas e arquivo"
        " 'folha_exercicios_alunos.txt' gerado para impressão!"
    )


if __name__ == "__main__":
    gerar_ambiente_treinamento()
