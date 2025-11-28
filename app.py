from flask import Flask, render_template
from main_logic import buscar_arbitragem

app = Flask(__name__)

@app.route("/")
def index():
    surebets = buscar_arbitragem()
    return render_template("index.html", surebets=surebets)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
