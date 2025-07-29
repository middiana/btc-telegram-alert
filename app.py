from flask import Flask, jsonify
from backtest import run_backtest

app = Flask(__name__)

@app.route("/run-backtest", methods=["GET"])
def backtest():
    result = run_backtest()
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
