from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import bsky_crawler
import rag_bot

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze_profile():
    data = request.json
    handle = data.get("handle")
    
    if not handle:
        return jsonify({"error": "No handle provided"}), 400

    # 1. 爬取数据
    print(f"🚀 Received request for: {handle}")
    clawler_result = bsky_crawler.get_profile_data(handle)
    
    if not clawler_result:
        return jsonify({"error": "Failed to fetch profile or profile not found"}), 404
        
    # 2. AI 分析
    text_content = clawler_result["full_text_for_analysis"]
    analysis_result = rag_bot.analyze_personality(text_content)
    
    # 3. 构造返回 (合并信息)
    response_data = {
        "profile": clawler_result["profile"],
        "analysis": analysis_result
    }
    
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
