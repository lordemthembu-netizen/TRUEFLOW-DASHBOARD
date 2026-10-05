"""
TRUEFLOW Dashboard application entry point.
"""

from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "TRUEFLOW Dashboard"


if __name__ == "__main__":
    app.run(debug=True)
