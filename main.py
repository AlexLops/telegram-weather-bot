import subprocess
import os
from flask import Flask

app = Flask(__name__)

LOG_FILE = "/tmp/summarizer_debug.log"

@app.route("/summarize")
def trigger_summarizer():
    """Manually trigger the summarizer and show debug output."""
    
    # Run summarizer script
    subprocess.run(["python3", "summarizer.py"], capture_output=True, text=True)

    # Read the debug log file
    try:
        with open(LOG_FILE, "r") as log:
            logs = log.read()
    except FileNotFoundError:
        logs = "❌ No log file found. Summarizer may not be running."

    return f"✅ Debug Logs:\n{logs}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
