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

// Função unificada e segura para alternar as abas da Portaria
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
            statusOperacao.portariaConcluida = true;
            statusOperacao.veiculoLiberado = data.doca;

            const luzPortaria = document.getElementById('luz-portaria');
            if (luzPortaria) luzPortaria.className = 'luz-status status-VERDE';

            const luzRecebimento = document.getElementById('luz-recebimento');
            if (luzRecebimento) luzRecebimento.className = 'luz-status status-AMARELO';

            fecharModal('modal-portaria');

            setTimeout(() => {
                alert(`🚦 Veículo direcionado para a doca.\nO setor de DOCA & CONFERÊNCIA foi LIBERADO!`);
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

            const luzRecebimento = document.getElementById('luz-recebimento');
            if (luzRecebimento) luzRecebimento.className = 'luz-status status-VERDE';

            const luzEstoque = document.getElementById('luz-estoque');
            if (luzEstoque) luzEstoque.className = 'luz-status status-AMARELO';

            fecharModal('modal-conferencia');
        }
    })
    .catch(err => console.error("Erro no recebimento:", err));
}