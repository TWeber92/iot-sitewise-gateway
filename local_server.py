from flask import Flask, request, jsonify
from src.common.router import route

app = Flask(__name__)


@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def handle(path):
    result = route(request.method, f"/{path}", request.get_data(as_text=True))
    return result["body"], result["statusCode"]


if __name__ == "__main__":
    app.run(port=5000, debug=True)
