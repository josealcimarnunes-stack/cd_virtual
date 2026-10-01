from flask import Flask, render_template
from rotas.portaria import portaria_bp
from rotas.conferencia import conferencia_bp  # Imports the new route
from rotas.estoque import estoque_bp

app = Flask(__name__)

app.register_blueprint(portaria_bp)
app.register_blueprint(conferencia_bp)  # Registers Blueprint
app.register_blueprint(estoque_bp)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
