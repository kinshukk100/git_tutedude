import os
import json
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask import redirect

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json.sort_keys = False


@app.route("/api")
def api():
    json_path = os.getenv("LOCAL_JSON_PATH", str(BASE_DIR / "data" / "books.json"))
    file_path = Path(json_path)

    if not file_path.is_absolute():
        file_path = BASE_DIR / file_path

    if not file_path.exists():
        return []

    with file_path.open("r", encoding="utf-8") as file:
        rows = json.load(file)

    data = []
    for row in rows if isinstance(rows, list) else []:
        item = {
            "title": row.get("title", ""),
            "author": row.get("author", ""),
        }
        data.append(item)

    return data


@app.route("/submit", methods=["POST"])
def submit():
    uri = os.getenv("MONGODB_URI", "")
    db_name = os.getenv("MONGODB_DB_NAME", "")
    collection_name = os.getenv("MONGODB_COLLECTION_NAME", "")

    if uri.strip() == "":
        return jsonify({"error": "ERROR: MONGODB_URI is missing in .env"}), 400

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()

    if title == "" or author == "":
        return jsonify({"error": "Title and author are required"}), 400

    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]
    collection.insert_one({"title": title, "author": author})
    client.close()

    return jsonify({"message": "ok"}), 200


@app.route("/form")
def form_page():
    return redirect("/form.html")


@app.route("/success")
def success_page():
    return redirect("/success.html")


if __name__ == "__main__":
    app.run(debug=True)
