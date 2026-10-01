import os
from flask import Flask, render_template
from rotas.portaria import portaria_bp
from rotas.conferencia import conferencia_bp

app = Flask(__name__)

# Registro das rotas modulares
app.register_blueprint(portaria_bp)
app.register_blueprint(conferencia_bp)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    # Capta a porta dinamica da Render ou usa 5000 para rodar localmente
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
