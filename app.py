from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

print("🚀 AI SERVER ĐANG KHỞI ĐỘNG...")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "Store AI - Simple Version",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_query = data.get('question', '').strip()
        
        if not user_query:
            return jsonify({"success": False, "error": "Câu hỏi không được để trống"}), 400
        
        # Response đơn giản
        response = f"🤖 AI: Tôi đã nhận câu hỏi '{user_query}'. Server đang hoạt động!"
        
        return jsonify({
            "success": True,
            "question": user_query,
            "answer": response,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("📍 Server: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
