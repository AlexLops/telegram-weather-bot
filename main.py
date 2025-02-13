from flask import Flask
import subprocess

app = Flask(__name__)

@app.route("/parse")
def trigger_parser():
    """Manually trigger the parser."""
    subprocess.run(["python3", "parser.py"])
    return "✅ Parser executed"

@app.route("/summarize")
def trigger_summarizer():
    """Manually trigger the summarizer."""
    subprocess.run(["python3", "summarizer.py"])
    return "✅ Summarizer executed"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
