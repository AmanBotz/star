from flask import Flask

app = Flask(__name__)

@app.route("/")
def health():
    return "OK", 200

if __name__ == "__main__":
    # Bind to all interfaces so Koyeb can reach it.
    app.run(host="0.0.0.0", port=8000)
