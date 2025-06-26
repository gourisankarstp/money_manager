from flask import Flask, request
from sqlite_to_sheet_project.main import main  # ✅ Correct import
import os  # 🔧 Required for reading PORT

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def handler():
    result, status = main(request)
    return result, status

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
