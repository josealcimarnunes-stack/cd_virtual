// ==========================================
// ESTADO GLOBAL DA SIMULAÇÃO (CONTROLE DE FLUXO)
// ==========================================
let statusOperacao = {
    portariaConcluida: false,
    recebimentoConcluido: false,
    veiculoLiberado: null
};

// ==========================================
// FUNÇÕES DE CONTROLE DE MODAL E SEGURANÇA
// ==========================================

// Abre o modal validando a sequência operacional obrigatoria
function abrirModalSeguro(idModal) {
    if (idModal === 'modal-conferencia' && !statusOperacao.portariaConcluida) {
        alert("⚠️ ACESSO NEGADO!\n\nVocê precisa primeiro realizar a Triagem, Pesagem e Liberação do veículo no módulo de PORTARIA.");
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
        placa: document.getElementById('port-placa').value,
        carreta: document.getElementById('port-carreta').value,
        motorista: document.getElementById('port-motorista').value,
        doc_motorista: document.getElementById('port-doc-motorista').value,
        tipo_veiculo: document.getElementById('port-tipo-veiculo').value,
        transportadora: document.getElementById('port-transportadora').value,
        peso_bruto: elPeso ? elPeso.innerText : '0 Kg',
        chk_lacre: document.getElementById('chk-lacre').checked,
        chk_bau: document.getElementById('chk-bau').checked,
        chk_epis: document.getElementById('chk-epis').checked,
        chave_danfe: document.getElementById('port-chave-danfe').value,
        po: document.getElementById('port-po').value,
        doca_destino: document.getElementById('port-doca-destino').value,
        pager: document.getElementById('port-pager').value
    };

    fetch('/api/portaria/processar-completo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    })
    .then(res => res.json())
    .then(data => {
        alert(data.mensagem);
        if (data.status === 'sucesso') {
            // Atualiza travas globais de fluxo
            statusOperacao.portariaConcluida = true;
            statusOperacao.veiculoLiberado = data.doca;

            // Atualiza a luz da Portaria
            const luzPortaria = document.getElementById('luz-portaria');
            if (luzPortaria) luzPortaria.className = 'luz-status status-VERDE';

            // Libera a luz da Doca para AMARELO (Pronto para operar)
            const luzRecebimento = document.getElementById('luz-recebimento');
            if (luzRecebimento) luzRecebimento.className = 'luz-status status-AMARELO';

            fecharModal('modal-portaria');

            setTimeout(() => {
                alert(`🚦 Veículo direcionado para a ${data.doca}.\nO setor de DOCA & CONFERÊNCIA foi LIBERADO!`);
            }, 300);
        }
    })
    .catch(err => console.error("Erro ao processar portaria:", err));
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
        doca: document.getElementById('doca-numero').value,
        calco_ok: document.getElementById('doca-calco').value,
        nivelador_ok: document.getElementById('doca-nivelador').value,
        qtd_avaria: document.getElementById('doca-qtd-avaria').value,
        tipo_avaria: document.getElementById('doca-tipo-avaria').value,
        obs_avaria: document.getElementById('doca-obs-avaria').value
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

            // Atualiza luzes de status
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
// ESTADO GLOBAL E MODO DEMO
// ==========================================
let modoDemo = false; // Se true, ignora todas as travas para navegação livre

function alternarModoDemo(ativado) {
    modoDemo = ativado;
    if (modoDemo) {
        alert("🔓 MODO DEMO ATIVADO!\n\nTodas as travas de segurança foram temporariamente desativadas para apresentação livre das telas.");
    } else {
        alert("🔒 MODO OPERACIONAL ATIVADO!\n\nAs travas sequenciais de segurança estão ativas.");
    }
}

// ==========================================
// ABERTURA DE MODAL COM SUPORTE AO MODO DEMO
// ==========================================
function abrirModalSeguro(idModal) {
    // Se o Modo Demo estiver ligado, libera o acesso direto a qualquer tela
    if (modoDemo) {
        document.getElementById(idModal).style.display = 'flex';
        return;
    }

    // Validações sequenciais normais quando o Modo Demo está DESLIGADO
    if (idModal === 'modal-conferencia' && !statusOperacao.portariaConcluida) {
        alert("⚠️ ACESSO NEGADO!\n\nVocê precisa primeiro realizar a Triagem, Pesagem e Liberação no módulo de PORTARIA.\n\n(Dica: Ative o 'Modo Apresentação' no topo para navegar livremente).");
        return;
    }

    if (idModal === 'modal-estoque' && !statusOperacao.recebimentoConcluido) {
        alert("⚠️ ACESSO NEGADO!\n\nConclua a Conferência e Recebimento na DOCA antes de acessar o WMS/Estoque.");
        return;
    }

    document.getElementById(idModal).style.display = 'flex';
}

// ==========================================
// VALIDAÇÃO ABA POR ABA DA PORTARIA (COM MODO DEMO)
// ==========================================
function mudarAbaPortaria(idAba) {
    // Se o Modo Demo estiver ligado, permite clicar em qualquer aba sem travas
    if (!modoDemo) {
        if (idAba === 'aba-balanca' && !fluxoPortaria.triagemOk) {
            alert("🛑 BLOQUEIO DE SEGURANÇA:\n\nConclua a TRIAGEM antes de ir para a Balança!");
            return;
        }
        if (idAba === 'aba-inspecao' && !fluxoPortaria.balancaOk) {
            alert("🛑 BLOQUEIO DE SEGURANÇA:\n\nA pesagem na BALANÇA ainda não foi realizada!");
            return;
        }
        if (idAba === 'aba-fiscal' && !fluxoPortaria.inspecaoOk) {
            alert("🛑 BLOQUEIO DE SEGURANÇA:\n\nVeículo pendente de APROVAÇÃO NA INSPEÇÃO FÍSICA!");
            return;
        }
        if (idAba === 'aba-pager' && !fluxoPortaria.fiscalOk) {
            alert("🛑 BLOQUEIO DE SEGURANÇA:\n\nValidação FISCAL/DANFE pendente!");
            return;
        }
    }

    // Troca de aba visual
    const abas = document.querySelectorAll('#modal-portaria .conteudo-aba');
    abas.forEach(aba => aba.style.display = 'none');

    const abaSelecionada = document.getElementById(idAba);
    if (abaSelecionada) abaSelecionada.style.display = 'block';

    const botoes = document.querySelectorAll('#modal-portaria .btn-aba');
    botoes.forEach(btn => btn.classList.remove('active'));
    if (event && event.target) event.target.classList.add('active');
}