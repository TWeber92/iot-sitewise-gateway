from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request
from src.common.router import route

app = Flask(__name__)


@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def handle(path):
    # Now this will return the body for GET requests too
    raw_body = request.stream.read().decode("utf-8")

    print(f"METHOD: {request.method}")
    print(f"BODY LENGTH: {len(raw_body)}")
    print(f"BODY: {raw_body!r}")

    result = route(request.method, f"/{path}", raw_body, headers=dict(request.headers))
    return result["body"], result["statusCode"]


if __name__ == "__main__":
    app.run(port=5000, debug=True)
