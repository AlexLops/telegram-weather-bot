import os
import subprocess
from flask import Flask

app = Flask(__name__)

@app.route("/parse")
def trigger_parser():
    """Manually trigger the parser."""
    result = subprocess.run(["python3", "parser.py"], capture_output=True, text=True)
    return f"✅ Parser executed:\n{result.stdout}"

@app.route("/summarize")
def trigger_summarizer():
    """Manually trigger the summarizer."""
    print('Trigger sum1!')
    result = subprocess.run(["python3", "summarizer.py"], capture_output=True, text=True)
    print('Trigger sum2!')
    return f"✅ Summarizer executed:\n{result.stdout}"

@app.route("/")
def home():
    return "Manual Trigger API: Use /parse or /summarize"

if __name__ == "__main__":
    print('Hi!')
    app.run(host="0.0.0.0", port=10000)

