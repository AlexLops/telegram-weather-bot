import subprocess
import os
from flask import Flask

app = Flask(__name__)

LOG_FILE = "/tmp/summarizer_debug.log"

@app.route("/summarize")
def trigger_summarizer():
    """Manually trigger the summarizer and capture errors."""
    
    try:
        result = subprocess.run(
            ["python3", "summarizer.py"],
            capture_output=True,
            text=True
        )
        
        # Log any error messages
        if result.stderr:
            return f"❌ Error running summarizer.py:\n{result.stderr}"

        # Read the debug log file (if it was created)
        try:
            with open(LOG_FILE, "r") as log:
                logs = log.read()
        except FileNotFoundError:
            logs = "❌ No log file found. Summarizer may not be running."

        return f"✅ Debug Logs:\n{logs}"
    
    except Exception as e:
        return f"❌ Exception while executing summarizer.py: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
