import os
from flask import Flask, render_template

# Importação dos Blueprints modulares
from rotas.portaria import portaria_bp
from rotas.conferencia import conferencia_bp
from rotas.compras import compras_bp  # <- NOVO: Módulo de Compras & Suprimentos

app = Flask(__name__)

# ============================================================
# Registro dos Blueprints (rotas modulares do CD Virtual)
# ============================================================
app.register_blueprint(portaria_bp)  # Portaria / Guarita
app.register_blueprint(conferencia_bp)  # Doca / Conferência Cega
app.register_blueprint(compras_bp)  # Compras & Suprimentos (Hub 3PL)


# ============================================================
# Rota Principal - Planta Baixa do CD Virtual
# ============================================================
@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# Execução
# ============================================================
if __name__ == "__main__":
    # Capta a porta dinâmica da Render ou usa 5000 para rodar localmente
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
