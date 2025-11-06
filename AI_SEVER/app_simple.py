# app_simple.py - Version đơn giản không cần database
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Mock data từ database của bạn
MOCK_PRODUCTS = [
    {
        "id": 1, 
        "name": "iPhone 15 128GB | Chính hãng VN/A", 
        "price": 99999999.99, 
        "sale_price": 160000000.00, 
        "stock_quantity": 10, 
        "category_name": "Điện thoại",
        "description": "Điện thoại Apple"
    },
    {
        "id": 2, 
        "name": "MacBook Air 13", 
        "price": 26990000.00, 
        "sale_price": 0.00, 
        "stock_quantity": 5, 
        "category_name": "Laptop",
        "description": "Laptop mỏng nhẹ"
    },
    {
        "id": 10, 
        "name": "iphone 16 promax", 
        "price": 22222222.00, 
        "sale_price": 22222222.00, 
        "stock_quantity": 4, 
        "category_name": "Điện thoại",
        "description": "1212"
    },
    {
        "id": 11, 
        "name": "Iphone 17 Promax 1T", 
        "price": 6500000.00, 
        "sale_price": 6500000.00, 
        "stock_quantity": 20, 
        "category_name": "Điện thoại",
        "description": "iPhone 17 Pro Max cao cấp"
    },
    {
        "id": 12, 
        "name": "Tai nghe Bluetooth Apple AirPods 4", 
        "price": 3790000.00, 
        "sale_price": 3500000.00, 
        "stock_quantity": 7, 
        "category_name": "Phụ kiện",
        "description": "Tai nghe không dây Apple"
    },
    {
        "id": 13, 
        "name": "Máy tính bảng Lenovo Idea Tab", 
        "price": 6000000.00, 
        "sale_price": 5500000.00, 
        "stock_quantity": 10, 
        "category_name": "Tablet",
        "description": "Máy tính bảng Android"
    }
]

class SimpleAIAssistant:
    def process_query(self, user_query):
        user_query = user_query.lower()
        
        # Simple rule-based responses
        if any(word in user_query for word in ["xin chào", "hello", "hi"]):
            return "Xin chào! Tôi là trợ lý AI của cửa hàng điện tử. Tôi có thể giúp gì cho bạn về sản phẩm, giá cả hoặc tồn kho?"
        
        elif "iphone" in user_query:
            iphones = [p for p in MOCK_PRODUCTS if "iphone" in p["name"].lower()]
            return self.format_products_response(iphones, "iPhone")
        
        elif "macbook" in user_query or "laptop" in user_query:
            laptops = [p for p in MOCK_PRODUCTS if "macbook" in p["name"].lower() or "laptop" in p["category_name"].lower()]
            return self.format_products_response(laptops, "Laptop")
        
        elif "airpods" in user_query or "tainghe" in user_query:
            airpods = [p for p in MOCK_PRODUCTS if "airpods" in p["name"].lower()]
            return self.format_products_response(airpods, "Tai nghe")
        
        elif "tablet" in user_query or "máy tính bảng" in user_query:
            tablets = [p for p in MOCK_PRODUCTS if "tablet" in p["category_name"].lower()]
            return self.format_products_response(tablets, "Máy tính bảng")
        
        elif any(word in user_query for word in ["giá", "bao nhiêu tiền", "cost", "price"]):
            return self.handle_price_query(user_query)
        
        elif any(word in user_query for word in ["còn hàng", "tồn kho", "stock", "có sẵn"]):
            return self.handle_stock_query(user_query)
        
        elif any(word in user_query for word in ["sản phẩm", "có gì", "mặt hàng"]):
            return self.list_all_products()
        
        elif any(word in user_query for word in ["khuyến mãi", "giảm giá", "sale"]):
            return self.list_discounted_products()
        
        else:
            return "Tôi có thể giúp gì cho bạn? Hãy hỏi tôi về sản phẩm, giá cả, khuyến mãi hoặc tình trạng tồn kho. Ví dụ: 'iPhone giá bao nhiêu?' hoặc 'Còn MacBook không?'"
    
    def format_products_response(self, products, category_name):
        if not products:
            return f"Hiện không có {category_name} nào trong kho."
        
        response = f"Các {category_name} hiện có:\n"
        for p in products:
            price_info = self.format_price(p)
            response += f"• {p['name']}: {price_info} | Tồn kho: {p['stock_quantity']} chiếc\n"
        return response
    
    def format_price(self, product):
        if product['sale_price'] and product['sale_price'] < product['price']:
            return f"{product['sale_price']:,.0f} VNĐ (Khuyến mãi từ {product['price']:,.0f} VNĐ)"
        else:
            return f"{product['price']:,.0f} VNĐ"
    
    def handle_price_query(self, user_query):
        for product in MOCK_PRODUCTS:
            if product["name"].lower() in user_query:
                price_info = self.format_price(product)
                return f"{product['name']} có giá {price_info}. Hiện còn {product['stock_quantity']} chiếc."
        
        return "Bạn muốn hỏi giá sản phẩm nào? Vui lòng cung cấp tên sản phẩm cụ thể như 'iPhone 15', 'MacBook Air', v.v."
    
    def handle_stock_query(self, user_query):
        for product in MOCK_PRODUCTS:
            if product["name"].lower() in user_query:
                status = "còn hàng" if product['stock_quantity'] > 0 else "hết hàng"
                return f"{product['name']} hiện {status} ({product['stock_quantity']} chiếc)."
        
        return "Bạn muốn kiểm tra tồn kho sản phẩm nào?"
    
    def list_all_products(self):
        response = "Danh sách tất cả sản phẩm:\n"
        for p in MOCK_PRODUCTS:
            price_info = self.format_price(p)
            response += f"• {p['name']}: {price_info} | Tồn kho: {p['stock_quantity']} chiếc\n"
        return response
    
    def list_discounted_products(self):
        discounted = [p for p in MOCK_PRODUCTS if p['sale_price'] and p['sale_price'] < p['price']]
        if not discounted:
            return "Hiện không có sản phẩm nào đang khuyến mãi."
        
        response = "Các sản phẩm đang khuyến mãi:\n"
        for p in discounted:
            discount = ((p['price'] - p['sale_price']) / p['price']) * 100
            response += f"• {p['name']}: {p['sale_price']:,.0f} VNĐ (Giảm {discount:.0f}% từ {p['price']:,.0f} VNĐ)\n"
        return response

# Khởi tạo AI
ai_assistant = SimpleAIAssistant()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "Store AI Assistant - Simple Version",
        "timestamp": datetime.now().isoformat(),
        "products_count": len(MOCK_PRODUCTS)
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_query = data.get('question', '').strip()
        
        if not user_query:
            return jsonify({
                "success": False,
                "error": "Câu hỏi không được để trống",
                "example_questions": [
                    "Có những iPhone nào?",
                    "MacBook Air giá bao nhiêu?",
                    "Sản phẩm nào đang khuyến mãi?",
                    "AirPods còn hàng không?"
                ]
            }), 400
        
        # Xử lý query
        ai_response = ai_assistant.process_query(user_query)
        
        return jsonify({
            "success": True,
            "question": user_query,
            "answer": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Lỗi xử lý: {str(e)}"
        }), 500

@app.route('/api/store-info', methods=['GET'])
def store_info():
    return jsonify({
        "store_context": {
            "products": MOCK_PRODUCTS,
            "total_products": len(MOCK_PRODUCTS),
            "categories": list(set(p["category_name"] for p in MOCK_PRODUCTS))
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/')
def home():
    return """
    <h1>🤖 Store AI Assistant</h1>
    <p>API Server đang chạy!</p>
    <p>Endpoints:</p>
    <ul>
        <li><code>POST /api/chat</code> - Chat với AI</li>
        <li><code>GET /api/health</code> - Health check</li>
        <li><code>GET /api/store-info</code> - Thông tin cửa hàng</li>
    </ul>
    """

if __name__ == '__main__':
    print("🚀 AI Server đang khởi chạy...")
    print("📍 Địa chỉ: http://localhost:5000")
    print("📚 Endpoints:")
    print("   POST http://localhost:5000/api/chat")
    print("   GET  http://localhost:5000/api/health")
    print("   GET  http://localhost:5000/api/store-info")
    print("\n🎯 Test ngay với:")
    print('   curl -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d "{\\"question\\": \\"Xin chào\\"}"')
    print("\n⏳ Server đang chạy...")
    app.run(host='0.0.0.0', port=5000, debug=True)