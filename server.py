from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import bsky_crawler
import profile_analyzer

app = Flask(__name__)
CORS(app)

# @app.route("/") removed - Frontend is now served by React/Vite

@app.route("/api/analyze", methods=["POST"])
def analyze_profile():
    data = request.json
    handle = data.get("handle")
    lang = data.get("lang", "cn") # Default to Chinese
    
    if not handle:
        return jsonify({"error": "No handle provided"}), 400

    # 1. Crawl Data
    print(f"Received request for: {handle}")
    clawler_result = bsky_crawler.get_profile_data(handle)
    
    if not clawler_result:
        return jsonify({"error": "Failed to fetch profile or profile not found"}), 404
        
    # 2. AI Analysis
    text_content = clawler_result["full_text_for_analysis"]
    analysis_result = profile_analyzer.analyze_personality(text_content, lang=lang)
    
    # 3. Construct Response (Merge Information)
    response_data = {
        "profile": clawler_result["profile"],
        "analysis": analysis_result
    }
    
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
