from __future__ import annotations

import json
from http import HTTPStatus
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request

from bubble import BubbleManager, InfoFetcher

app = Flask(__name__)
manager = BubbleManager()


@app.route("/")
def index() -> str:
    return render_template("index.html")


def _serialize_bubbles() -> Dict[str, Any]:
    return {"bubbles": [bubble.to_dict() for bubble in manager.bubbles]}


@app.route("/api/health", methods=["GET"])
def health() -> Any:
    """轻量化健康检查，便于前端识别后端是否在线。"""

    return jsonify({"status": "ok", "count": len(manager.bubbles)})


@app.route("/api/bubbles", methods=["GET", "POST"])
def bubbles() -> Any:
    if request.method == "GET":
        return jsonify(_serialize_bubbles())

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    idea = (data.get("idea") or "").strip()
    if not title or not idea:
        return (
            jsonify({"error": "标题和想法内容都不能为空"}),
            HTTPStatus.BAD_REQUEST,
        )

    bubble = manager.create_bubble(title=title, idea=idea)
    return jsonify({"bubble": bubble.to_dict()})


@app.route("/api/bubbles/<int:bubble_id>/fetch", methods=["POST"])
def fetch_info(bubble_id: int) -> Any:
    bubble = manager.find_bubble(bubble_id)
    if not bubble:
        return jsonify({"error": "未找到对应的 Bubble"}), HTTPStatus.NOT_FOUND

    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()
    if not query:
        return (
            jsonify({"error": "请输入检索关键词"}),
            HTTPStatus.BAD_REQUEST,
        )

    resources = InfoFetcher.fetch(query)
    manager.attach_resources(bubble, resources)
    return jsonify({"bubble": bubble.to_dict(), "resources": resources})


@app.errorhandler(404)
def not_found(_error: Exception) -> Any:
    return render_template("404.html"), HTTPStatus.NOT_FOUND


if __name__ == "__main__":
    port = int((Path(".env.json").exists() and json.loads(Path(".env.json").read_text()).get("PORT")) or 5000)
    app.run(host="0.0.0.0", port=port, debug=False)
