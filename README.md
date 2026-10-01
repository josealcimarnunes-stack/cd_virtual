# 🚚 CD Virtual — Simulador de Operações Logísticas & WMS

O **CD Virtual** é um simulador interativo de Centro de Distribuição desenvolvido para automatizar, validar e controlar o fluxo operacional de cargas industriais. 

O sistema foi projetado com foco em **processos reais de chão de fábrica**, implementando travas de segurança encadeadas para impedir divergências de dados entre a chegada do veículo e o recebimento da mercadoria.

---

## 🚦 Fluxo da Operação

1. **Portaria & Balança Rodoviária:**
   - Triagem e identificação (Motorista, Veículo, Transportadora).
   - Pesagem bruta automatizada e validação de excesso de peso.
   - Checklist rigoroso de inspeção física (Lacre, EPIs, baú e integridade).
   - Validação fiscal (Chave DANFE / CT-e e Pedido de Compra).
   - Gestão de pátio e direcionamento para doca por Pager.

2. **Doca & Recebimento:**
   - Trava de segurança operacional (Calço de roda e nivelador de doca).
   - Conferência cega via bipagem de código de barras (EAN-13 / DUN-14).
   - Apontamento e fotos de avarias / não-conformidades.

3. **WMS & Armazém:**
   - Sugestão automatizada de endereçamento (*Putaway*) por rua, prateleira e nível.

---

## 🛠️ Tecnologias Utilizadas

* **Back-end:** Python, Flask (Arquitetura Modular com Blueprints)
* **Front-end:** HTML5, CSS3, JavaScript (ES6+ assíncrono com Fetch API)
* **Servidor de Produção:** Gunicorn / Render
* **Banco de Dados:** SQLite

---

## 🚀 Como Rodar o Projeto Localmente

```bash
# 1. Clone o repositório
git clone [https://github.com/SEU-USUARIO/cd-virtual.git](https://github.com/SEU-USUARIO/cd-virtual.git)

# 2. Acesse a pasta do projeto
cd cd-virtual

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a aplicação
python app.py