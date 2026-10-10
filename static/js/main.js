// ==========================================
// ESTADO GLOBAL DA SIMULAÇÃO (CONTROLE DE FLUXO)
// ==========================================
let statusOperacao = {
    portariaConcluida: false,
    recebimentoConcluido: false,
    veiculoLiberado: null
};

let modoDemo = false; // Se true, ignora todas as travas para navegação livre


// ==========================================
// FUNÇÕES DE CONTROLE DE MODAL E SEGURANÇA
// ==========================================

function alternarModoDemo(ativado) {
    modoDemo = ativado;
    if (modoDemo) {
        alert("🔓 MODO DEMO ATIVADO!\n\nTodas as travas de segurança foram temporariamente desativadas para apresentação livre das telas.");
    } else {
        alert("🔒 MODO OPERACIONAL ATIVADO!\n\nAs travas sequenciais de segurança estão ativas.");
    }
}

// Abre o modal validando a sequência operacional obrigatória ou o Modo Demo
function abrirModalSeguro(idModal) {
    if (modoDemo) {
        document.getElementById(idModal).style.display = 'flex';
        return;
    }

    if (idModal === 'modal-conferencia' && !statusOperacao.portariaConcluida) {
        alert("⚠️ ACESSO NEGADO!\n\nVocê precisa primeiro realizar a Triagem, Pesagem e Liberação do veículo no módulo de PORTARIA.\n\n(Dica: Ative o 'Modo Apresentação' no topo para navegar livremente).");
        return;
    }

    if (idModal === 'modal-estoque' && !statusOperacao.recebimentoConcluido) {
        alert("⚠️ ACESSO NEGADO!\n\nVocê precisa concluir a Conferência e Recebimento do material na DOCA antes de acessar o Estoque/WMS.");
        return;
    }

    document.getElementById(idModal).style.display = 'flex';
}

function abrirModal(idModal) {
    document.getElementById(idModal).style.display = 'flex';
}

function fecharModal(idModal) {
    document.getElementById(idModal).style.display = 'none';
}


// ==========================================
// MÓDULO 1: PORTARIA & BALANÇA
// ==========================================

function mudarAbaPortaria(idAba) {
    const abas = document.querySelectorAll('#modal-portaria .conteudo-aba');
    abas.forEach(aba => aba.style.display = 'none');

    const abaSelecionada = document.getElementById(idAba);
    if (abaSelecionada) {
        abaSelecionada.style.display = 'block';
    }

    const botoes = document.querySelectorAll('#modal-portaria .btn-aba');
    botoes.forEach(btn => btn.classList.remove('active'));
    if (event && event.target) {
        event.target.classList.add('active');
    }
}

function capturarPesoEntrada() {
    const pesosSimulados = [38450, 41200, 42850, 45100];
    const pesoSorteado = pesosSimulados[Math.floor(Math.random() * pesosSimulados.length)];
    const el = document.getElementById('display-peso-bruto');
    if (el) el.innerText = `${pesoSorteado.toLocaleString('pt-BR')} Kg`;
    alert(`📡 Balança Rodoviária 01: Peso capturado com sucesso (${pesoSorteado} Kg)`);
}

function processarPortariaCompleta() {
    const elPeso = document.getElementById('display-peso-bruto');

    const dados = {
        placa: document.getElementById('port-placa').value.trim(),
        carreta: document.getElementById('port-carreta').value.trim(),
        motorista: document.getElementById('port-motorista').value.trim(),
        doc_motorista: document.getElementById('port-doc-motorista').value.trim(),
        tipo_veiculo: document.getElementById('port-tipo-veiculo')?.value || '',
        transportadora: document.getElementById('port-transportadora')?.value || '',
        peso_bruto: elPeso ? elPeso.innerText : '0 Kg',
        po: document.getElementById('port-po').value.trim(),
        chave_danfe: document.getElementById('port-chave-danfe')?.value || '',
        doca_destino: document.getElementById('port-doca-destino')?.value || '',
        pager: document.getElementById('port-pager')?.value || '',
        chk_lacre: document.getElementById('chk-lacre').checked,
        chk_bau: document.getElementById('chk-bau').checked,
        chk_epis: document.getElementById('epi-oculos').checked &&
                  document.getElementById('epi-botina').checked &&
                  document.getElementById('epi-capacete').checked &&
                  document.getElementById('epi-colete').checked
    };

    fetch('/api/portaria/processar-completo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    })
    .then(async res => {
        const resultado = await res.json();

        if (!res.ok) {
            exibirPainelQuiz(resultado.mensagem, resultado.falha_real);
            return;
        }

        alert(resultado.mensagem);
        statusOperacao.portariaConcluida = true;
        statusOperacao.veiculoLiberado = resultado.doca || null;

        const luzPortaria = document.getElementById('luz-portaria');
        if (luzPortaria) luzPortaria.className = 'luz-status status-VERDE';

        const luzRecebimento = document.getElementById('luz-recebimento');
        if (luzRecebimento) luzRecebimento.className = 'luz-status status-AMARELO';

        fecharModal('modal-portaria');

        setTimeout(() => {
            alert("🚦 Veículo direcionado para a doca.\nO setor de DOCA & CONFERÊNCIA foi LIBERADO!");
        }, 300);
    })
    .catch(err => console.error("Erro na requisição da portaria:", err));
}

function exibirPainelQuiz(mensagemErro, falhaReal) {
    const painelQuiz = document.getElementById('painel-quiz-diagnostico');
    const msgAlerta = document.getElementById('quiz-mensagem-alerta');

    if (painelQuiz && msgAlerta) {
        msgAlerta.innerText = mensagemErro;
        painelQuiz.style.display = 'block';
        painelQuiz.dataset.falhaReal = falhaReal;
    } else {
        alert(mensagemErro);
    }
}

function enviarDiagnosticoQuiz() {
    const painelQuiz = document.getElementById('painel-quiz-diagnostico');
    const falhaReal = painelQuiz.dataset.falhaReal;

    const opcaoSelecionada = document.querySelector('input[name="diagnostico"]:checked');
    if (!opcaoSelecionada) {
        alert("⚠️ Selecione uma das alternativas do quiz antes de enviar a auditoria.");
        return;
    }

    const respostaEscolhida = opcaoSelecionada.value;

    fetch('/api/portaria/validar-diagnostico', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            falha_real: falhaReal,
            resposta_escolhida: respostaEscolhida
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.mensagem);
        if (data.acertou) {
            painelQuiz.style.display = 'none';
            statusOperacao.portariaConcluida = true;

            const luzPortaria = document.getElementById('luz-portaria');
            if (luzPortaria) luzPortaria.className = 'luz-status status-VERDE';

            const luzRecebimento = document.getElementById('luz-recebimento');
            if (luzRecebimento) luzRecebimento.className = 'luz-status status-AMARELO';

            fecharModal('modal-portaria');
        }
    })
    .catch(err => console.error("Erro ao validar quiz:", err));
}


// ==========================================
// MÓDULO 2: DOCA & RECEBIMENTO
// ==========================================

function mudarAbaDoca(idAba) {
    const abas = document.querySelectorAll('#modal-conferencia .conteudo-aba-doca');
    abas.forEach(aba => aba.style.display = 'none');

    const abaSelecionada = document.getElementById(idAba);
    if (abaSelecionada) {
        abaSelecionada.style.display = 'block';
    }

    const botoes = document.querySelectorAll('#modal-conferencia .btn-aba-doca');
    botoes.forEach(btn => btn.classList.remove('active'));
    if (event && event.target) {
        event.target.classList.add('active');
    }
}

let contadorBipagem = 120;
function biparItem() {
    const barcode = document.getElementById('doca-barcode').value;
    if (!barcode) {
        alert("Por favor, insira ou bipe um código de barras válido.");
        return;
    }
    contadorBipagem += 1;
    const elQtd = document.getElementById('qtd-bipada-1');
    if (elQtd) elQtd.innerText = `${contadorBipagem} cx`;

    const input = document.getElementById('doca-barcode');
    if (input) {
        input.style.backgroundColor = '#1c3d27';
        setTimeout(() => { input.style.backgroundColor = ''; }, 300);
    }
}

function finalizarRecebimentoDoca() {
    const dados = {
        doca: document.getElementById('doca-numero')?.value || '',
        calco_ok: document.getElementById('doca-calco')?.value || '',
        nivelador_ok: document.getElementById('doca-nivelador')?.value || '',
        qtd_avaria: document.getElementById('doca-qtd-avaria')?.value || '0',
        tipo_avaria: document.getElementById('doca-tipo-avaria')?.value || '',
        obs_avaria: document.getElementById('doca-obs-avaria')?.value || ''
    };

    fetch('/api/conferencia/finalizar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    })
    .then(res => res.json())
    .then(data => {
        alert(data.mensagem);
        if (data.status === 'sucesso') {
            statusOperacao.recebimentoConcluido = true;

            const luzRecebimento = document.getElementById('luz-recebimento');
            if (luzRecebimento) luzRecebimento.className = 'luz-status status-VERDE';

            const luzEstoque = document.getElementById('luz-estoque');
            if (luzEstoque) luzEstoque.className = 'luz-status status-AMARELO';

            fecharModal('modal-conferencia');
        }
    })
    .catch(err => console.error("Erro no recebimento:", err));
}


// ==========================================
// MÓDULO 0: COMPRAS & SUPRIMENTOS (HUB 3PL)
// ==========================================

function carregarInsumosCategoria(categoria) {
    const painel = document.getElementById('painelInsumosDetalhados');
    const titulo = document.getElementById('tituloCategoriaSelecionada');
    const corpoTabela = document.getElementById('corpoTabelaInsumos');

    painel.style.display = 'block';

    const nomesCategorias = {
        'carga_seca': '📦 Carga Seca & Embalagens',
        'molhados_quimicos': '🧪 Molhados & Químicos',
        'pereciveis': '❄️ Perecíveis & Refrigerados',
        'apoio_infra': '🏢 Apoio & Infraestrutura do CD'
    };

    titulo.innerText = nomesCategorias[categoria] || 'Insumos Mapeados';

    fetch(`/api/compras/insumos/${categoria}`)
        .then(response => response.json())
        .then(data => {
            corpoTabela.innerHTML = '';
            document.getElementById('badgeTotalItens').innerText = `${data.insumos.length} Insumos`;

            data.insumos.forEach(item => {
                const critico = item.saldo < item.demanda;
                const statusBadge = critico
                    ? `<span style="background:#d32f2f; color:#fff; padding:2px 8px; border-radius:10px; font-size:11px;">🔴 Faltam ${item.demanda - item.saldo}</span>`
                    : `<span style="background:#388e3c; color:#fff; padding:2px 8px; border-radius:10px; font-size:11px;">🟢 OK</span>`;

                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid #2a2a40';
                tr.innerHTML = `
                    <td style="padding:6px;"><strong>${item.nome_insumo}</strong></td>
                    <td style="padding:6px; color:#00bcd4; font-size:12px;">${item.fornecedor}</td>
                    <td style="padding:6px; text-align:center;">${item.saldo} ${item.unidade}</td>
                    <td style="padding:6px; text-align:center;">${item.demanda} ${item.unidade}</td>
                    <td style="padding:6px; text-align:center;">${statusBadge}</td>
                    <td style="padding:6px; text-align:center;">
                        <button onclick="gerarPOInsumo(${item.id}, '${item.nome_insumo}', '${item.fornecedor}', '${categoria}')"
                            style="background:#ffea00; color:#000; border:none; padding:5px 10px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:11px;">
                            Emitir PO
                        </button>
                    </td>
                `;
                corpoTabela.appendChild(tr);
            });
        })
        .catch(err => console.error("Erro ao carregar insumos:", err));
}

function gerarPOInsumo(idInsumo, nomeInsumo, fornecedor, categoria) {
    const qtd = prompt(`Quantidade de [${nomeInsumo}] a comprar de [${fornecedor}]:`, "100");
    if (!qtd || isNaN(qtd) || parseInt(qtd) <= 0) return;

    fetch('/api/compras/emitir-po', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            insumo_id: idInsumo,
            nome_insumo: nomeInsumo,
            fornecedor: fornecedor,
            quantidade: parseInt(qtd),
            categoria: categoria
        })
    })
    .then(res => res.json())
    .then(res => {
        alert(`✅ Ordem de Compra ${res.codigo_po} emitida e gravada no SQLite!\nData: ${res.data_emissao}`);
        if (document.getElementById('painelPedidosFeitos')?.style.display === 'block') {
            carregarHistoricoPOs();
        }
    })
    .catch(err => alert("Erro ao emitir PO: " + err));
}


// ==========================================
// MÓDULO 0.5: PAINEL DE PEDIDOS FEITOS
// ==========================================

function abrirPainelPedidos() {
    const painel = document.getElementById('painelPedidosFeitos');
    painel.style.display = 'block';
    carregarHistoricoPOs();
    painel.scrollIntoView({ behavior: 'smooth' });
}

function fecharPainelPedidos() {
    document.getElementById('painelPedidosFeitos').style.display = 'none';
}

function carregarHistoricoPOs() {
    const corpo = document.getElementById('corpoPainelPedidos');
    if (!corpo) return;

    corpo.innerHTML = '<tr><td colspan="8" style="text-align:center; color:#666; padding:15px;">Carregando...</td></tr>';

    const catFiltro = document.getElementById('filtro-categoria')?.value || 'todas';
    const stFiltro = document.getElementById('filtro-status')?.value || 'todos';

    fetch(`/api/compras/historico?categoria=${catFiltro}&status=${stFiltro}`)
        .then(res => res.json())
        .then(lista => {
            corpo.innerHTML = '';

            if (!lista || lista.length === 0) {
                corpo.innerHTML = '<tr><td colspan="8" style="text-align:center; color:#666; padding:15px;">Nenhuma PO encontrada com os filtros atuais.</td></tr>';
                return;
            }

            const nomesCat = {
                'carga_seca': '📦 Carga Seca',
                'molhados_quimicos': '🧪 Molhados',
                'pereciveis': '❄️ Perecíveis',
                'apoio_infra': '🏢 Apoio',
                'nao_informada': '—'
            };

            lista.forEach(po => {
                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid #2a2a40';
                tr.innerHTML = `
                    <td style="padding:6px; color:#ffea00; font-weight:bold;">${po.codigo_po}</td>
                    <td style="padding:6px; font-size:12px;">${po.data_emissao || '—'}</td>
                    <td style="padding:6px; font-size:12px;">${nomesCat[po.categoria] || po.categoria || '—'}</td>
                    <td style="padding:6px;">${po.nome_insumo}</td>
                    <td style="padding:6px; color:#00bcd4; font-size:12px;">${po.fornecedor}</td>
                    <td style="padding:6px; text-align:center;">${po.quantidade}</td>
                    <td style="padding:6px; text-align:center; font-size:11px; color:#00ffcc;">${po.status}</td>
                    <td style="padding:6px; text-align:center; white-space:nowrap;">
                        <a href="/api/compras/download/${po.codigo_po}"
                           title="Baixar PO em TXT"
                           style="background:#ffea00; color:#000; padding:4px 8px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:11px; margin-right:3px;">
                           📥
                        </a>
                        <button onclick="copiarParaEmail('${po.codigo_po}')"
                           title="Copiar texto formatado para e-mail"
                           style="background:#00bcd4; color:#000; border:none; padding:4px 8px; border-radius:4px; cursor:pointer; font-weight:bold; font-size:11px;">
                           📧
                        </button>
                    </td>
                `;
                corpo.appendChild(tr);
            });
        })
        .catch(err => {
            console.error("Erro ao carregar histórico:", err);
            corpo.innerHTML = '<tr><td colspan="8" style="text-align:center; color:#d32f2f;">Erro ao carregar histórico.</td></tr>';
        });
}

function copiarParaEmail(codigoPo) {
    fetch(`/api/compras/copiar/${codigoPo}`)
        .then(res => res.json())
        .then(data => {
            if (data.texto) {
                navigator.clipboard.writeText(data.texto).then(() => {
                    alert(`✅ Texto da PO ${codigoPo} copiado!\n\nAgora cole no seu e-mail (Ctrl+V) e envie para o fornecedor.`);
                }).catch(() => {
                    const textarea = document.createElement('textarea');
                    textarea.value = data.texto;
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textarea);
                    alert(`✅ Texto da PO ${codigoPo} copiado!`);
                });
            }
        })
        .catch(err => alert("Erro ao copiar PO: " + err));
}


// ==========================================
// FUNÇÕES DE ABRIR E PREENCHER KPIS
// ==========================================

function abrirModalOTIF() {
    abrirModal('modal-kpi-otif');
    fetch('/api/kpi/detalhes-otif')
        .then(res => res.json())
        .then(lista => {
            const corpo = document.getElementById('tabela-kpi-otif-corpo');
            corpo.innerHTML = '';
            lista.forEach(f => {
                let badgeStrike = '🟢 0 Strikes (OK)';
                if (f.strikes === 1) badgeStrike = '🟡 1 Strike (Leve)';
                if (f.strikes === 2) badgeStrike = '🟠 2 Strikes (Alerta)';
                if (f.strikes >= 3) badgeStrike = '🔴 3 Strikes (GRAVE)';

                let badgeStatus = `<span style="background:#28a745; color:#fff; padding:2px 8px; border-radius:10px; font-size:11px;">HOMOLOGADO</span>`;
                if (f.status === 'EM_ALERTA') badgeStatus = `<span style="background:#ffaa00; color:#000; padding:2px 8px; border-radius:10px; font-size:11px;">EM ALERTA</span>`;
                if (f.status === 'BANIDO_OTIF' || f.strikes >= 3) badgeStatus = `<span style="background:#d32f2f; color:#fff; padding:2px 8px; border-radius:10px; font-size:11px;">🚫 BANIDO (OTIF)</span>`;

                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid #2a2a40';
                tr.innerHTML = `
                    <td style="padding:8px;"><a href="javascript:void(0)" onclick="inspecionarFornecedor('${f.nome}')" style="color:#00ffcc; text-decoration:underline; font-weight:bold;">${f.nome}</a></td>
                    <td style="padding:8px; color:#aaa;">${f.categoria}</td>
                    <td style="padding:8px; text-align:center; font-weight:bold; color:#00ffcc;">${f.otif_score}%</td>
                    <td style="padding:8px; text-align:center;">${badgeStrike}</td>
                    <td style="padding:8px; text-align:center;">${badgeStatus}</td>
                `;
                corpo.appendChild(tr);
            });
        });
}

function abrirModalGiroEstoque() {
    abrirModal('modal-kpi-giro');
    carregarGiroEstoque('semanal');
}

function carregarGiroEstoque(periodo) {
    // Destaca o botão ativo e atualiza link de download específico do período
    const botoes = document.querySelectorAll('#modal-kpi-giro .btn-filtro-giro');
    botoes.forEach(btn => {
        if (btn.dataset.periodo === periodo) {
            btn.style.background = '#00bcd4';
            btn.style.color = '#000';
            btn.style.fontWeight = 'bold';
        } else {
            btn.style.background = '#3d3d5c';
            btn.style.color = '#fff';
            btn.style.fontWeight = 'normal';
        }
    });

    const badgePeriodo = document.getElementById('badge-periodo-atual');
    if (badgePeriodo) badgePeriodo.innerText = `Filtro Ativo: PERÍODO ${periodo.toUpperCase()}`;

    const btnDownload = document.getElementById('btn-download-giro');
    if (btnDownload) btnDownload.href = `/api/kpi/exportar-giro-csv/${periodo}`;

    fetch(`/api/kpi/detalhes-giro/${periodo}`)
        .then(res => res.json())
        .then(data => {
            const corpo = document.getElementById('tabela-kpi-giro-corpo');
            corpo.innerHTML = '';
            data.itens.forEach(item => {
                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid #2a2a40';
                tr.innerHTML = `
                    <td style="padding:8px;"><strong>${item.insumo}</strong></td>
                    <td style="padding:8px; text-align:center; color:#00bcd4;">${item.posicao}</td>
                    <td style="padding:8px; text-align:center; color:#ffaa00;">${item.dias_imobilizado} dias</td>
                    <td style="padding:8px; text-align:center;">${item.qtd} un</td>
                    <td style="padding:8px; text-align:center;">${item.status}</td>
                `;
                corpo.appendChild(tr);
            });
        });
}

function abrirModalAcuracia() {
    abrirModal('modal-kpi-acuracia');
    fetch('/api/kpi/detalhes-acuracia')
        .then(res => res.json())
        .then(lista => {
            const corpo = document.getElementById('tabela-kpi-acuracia-corpo');
            corpo.innerHTML = '';
            lista.forEach(item => {
                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid #2a2a40';
                tr.innerHTML = `
                    <td style="padding:8px; font-size:12px; color:#aaa;">${item.data}</td>
                    <td style="padding:8px; font-weight:bold; color:#ffea00;">${item.po}</td>
                    <td style="padding:8px;">${item.insumo}</td>
                    <td style="padding:8px; text-align:center; color:#00ffcc;">${item.esperado_contado}</td>
                    <td style="padding:8px; color:#ff4444;">${item.motivo}</td>
                `;
                corpo.appendChild(tr);
            });
        });
}


// ==========================================
// AUDITORIA INDIVIDUAL DO FORNECEDOR (CLIQUE)
// ==========================================
function inspecionarFornecedor(nomeFornecedor) {
    fetch(`/api/kpi/fornecedor-detalhes/${nomeFornecedor}`)
        .then(res => res.json())
        .then(data => {
            const forn = data.fornecedor;
            const pos = data.historico_pos;

            let textoHtml = `
                <div style="background:#1a1a2e; padding:15px; border-radius:6px; border:1px solid #ffaa00; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h4 style="color:#ffaa00; margin:0 0 5px 0;">🏢 Auditoria de Fornecedor: ${forn.nome}</h4>
                        <p style="margin:3px 0; font-size:13px; color:#aaa;">Categoria: ${forn.categoria || 'Geral'}</p>
                        <p style="margin:3px 0; font-size:13px; color:#ff4444;"><strong>Total de Strikes:</strong> ${forn.strikes} | <strong>Status:</strong> ${forn.status}</p>
                    </div>
                    <div>
                        <a href="/api/kpi/exportar-fornecedor-csv/${encodeURIComponent(forn.nome)}" style="background:#00ffcc; color:#000; padding:8px 12px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:12px;">
                            📥 Baixar Relatório (CSV)
                        </a>
                    </div>
                </div>
                <h5 style="color:#00ffcc; margin-bottom:8px;">📦 Histórico de Ordens de Compra (POs) Vinculadas:</h5>
                <table style="width:100%; border-collapse:collapse; font-size:12px;">
                    <thead>
                        <tr style="color:#aaa; border-bottom:1px solid #3d3d5c;">
                            <th style="text-align:left; padding:5px;">Código PO</th>
                            <th style="text-align:left; padding:5px;">Data</th>
                            <th style="text-align:left; padding:5px;">Insumo</th>
                            <th style="text-align:center; padding:5px;">Qtd</th>
                            <th style="text-align:center; padding:5px;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            if (pos.length === 0) {
                textoHtml += `<tr><td colspan="5" style="text-align:center; color:#666; padding:10px;">Nenhuma PO registrada para este fornecedor.</td></tr>`;
            } else {
                pos.forEach(p => {
                    textoHtml += `
                        <tr style="border-bottom:1px solid #2a2a40;">
                            <td style="padding:5px; color:#ffea00; font-weight:bold;">${p.codigo_po}</td>
                            <td style="padding:5px;">${p.data_emissao || '—'}</td>
                            <td style="padding:5px;">${p.nome_insumo}</td>
                            <td style="padding:5px; text-align:center;">${p.quantidade}</td>
                            <td style="padding:5px; text-align:center; color:#00ffcc;">${p.status}</td>
                        </tr>
                    `;
                });
            }

            textoHtml += `</tbody></table>`;

            let modalDiv = document.getElementById('modal-auditoria-fornecedor');
            if (!modalDiv) {
                modalDiv = document.createElement('div');
                modalDiv.id = 'modal-auditoria-fornecedor';
                modalDiv.className = 'modal-overlay';
                document.body.appendChild(modalDiv);
            }

            modalDiv.innerHTML = `
                <div class="modal-conteudo" style="width: 780px; max-height: 80vh; overflow-y: auto;">
                    <span class="fechar-btn" onclick="document.getElementById('modal-auditoria-fornecedor').style.display='none'">&times;</span>
                    ${textoHtml}
                </div>
            `;
            modalDiv.style.display = 'flex';
        })
        .catch(err => alert("Erro ao carregar dados do fornecedor: " + err));
}