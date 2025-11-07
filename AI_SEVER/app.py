# Tệp: AI_SEVER/app.py
# Đã nâng cấp để sử dụng PostgreSQL (Neon) thay vì MySQL

import os
import psycopg2 # <-- Thư viện mới
import psycopg2.extras # <-- Thư viện mới để lấy dữ liệu dạng Dictionary
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime

# --- Cấu hình (Config) ---
app = Flask(__name__)
CORS(app)

# Lấy URL kết nối Neon từ biến môi trường của Render
DATABASE_URL = os.getenv('DATABASE_URL') 
# Lấy URL của Ollama
OLLAMA_URL = os.getenv('OLLAMA_HOST', 'http://ollama:11434')

print("🚀 AI SERVER ĐANG KHỞI ĐỘNG...")
if not DATABASE_URL:
    print("❌ LỖI NGHIÊM TRỌNG: Biến môi trường 'DATABASE_URL' chưa được cài đặt.")

# --- Lớp AI Chính ---

class StoreAIAssistant:
    def __init__(self):
        self.db = self.connect_db()
        if self.db:
            print("✅ Đã kết nối thành công đến Neon (PostgreSQL)!")
        
    def connect_db(self):
        """Kết nối đến database PostgreSQL (Neon)"""
        if not DATABASE_URL:
            print("❌ Lỗi kết nối: DATABASE_URL không tồn tại.")
            return None
        try:
            # Kết nối bằng URL từ Render
            return psycopg2.connect(DATABASE_URL)
        except Exception as e:
            # Ghi lại lỗi đầy đủ vào Logs của Render
            print(f"❌ Lỗi kết nối Database Neon nghiêm trọng: {e}")
            return None
    
    def get_store_context(self):
        """Lấy toàn bộ context cửa hàng cho AI"""
        if not self.db:
            return "Không thể kết nối database"
        
        try:
            # Sử dụng 'psycopg2.extras.DictCursor' để lấy kết quả dạng dictionary
            # (tương đương 'dictionary=True' của MySQL)
            cursor = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Lấy sản phẩm với categories (SQL vẫn tương thích)
            cursor.execute("""
                SELECT p.id, p.name, p.price, p.sale_price, p.stock_quantity, 
                       p.description, c.name as category_name
                FROM products p 
                LEFT JOIN categories c ON p.category_id = c.id 
                WHERE p.stock_quantity > 0
                ORDER BY p.id
            """)
            products = cursor.fetchall()
            
            # Lấy categories
            cursor.execute("SELECT id, name FROM categories WHERE status = 1")
            categories = cursor.fetchall()
            
            # Lấy sản phẩm bán chạy (dựa trên order_details)
            cursor.execute("""
                SELECT p.id, p.name, SUM(od.quantity) as total_sold
                FROM products p 
                JOIN order_details od ON p.id = od.product_id 
                GROUP BY p.id 
                ORDER BY total_sold DESC 
                LIMIT 5
            """)
            popular_products = cursor.fetchall()
            
            cursor.close()
            
            return {
                'products': products,
                'categories': categories,
                'popular_products': popular_products,
                'total_products': len(products),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            # Nếu kết nối bị mất, thử kết nối lại
            print(f"Lỗi lấy dữ liệu: {e}. Đang thử kết nối lại...")
            self.db = self.connect_db() # Thử kết nối lại
            return f"Lỗi lấy dữ liệu: {str(e)}"
    
    def create_smart_prompt(self, user_query, db_context):
        """Tạo prompt thông minh cho AI (Không thay đổi)"""
        
        # Kiểm tra nếu db_context là một chuỗi lỗi
        if isinstance(db_context, str):
            return f"Không thể lấy thông tin cửa hàng: {db_context}. Hãy báo cho khách hàng."

        # Format products info
        products_text = "\n".join([
            f"- {p['name']} (ID:{p['id']}): {self.format_price(p)} | Tồn kho: {p['stock_quantity']} | Danh mục: {p['category_name']}"
            for p in db_context.get('products', [])[:15] # Giới hạn để prompt không quá dài
        ])
        
        # Format categories
        categories_text = ", ".join([c['name'] for c in db_context.get('categories', [])])
        
        # Format popular products
        popular_text = "\n".join([
            f"- {p['name']}: Đã bán {p['total_sold']} sản phẩm"
            for p in db_context.get('popular_products', [])
        ])
        
        prompt = f"""
Bạn là trợ lý AI thân thiện cho cửa hàng điện tử. Hãy trả lời câu hỏi dựa trên thông tin cửa hàng dưới đây:

=== THÔNG TIN CỬA HÀNG ===
TỔNG SỐ SẢN PHẨM: {db_context.get('total_products', 0)}

DANH MỤC: {categories_text}

SẢN PHẨM:
{products_text}

SẢN PHẨM BÁN CHẠY:
{popular_text}

=== HƯỚNG DẪN TRẢ LỜI ===
1. TRẢ LỜI BẰNG TIẾNG VIỆT, thân thiện, nhiệt tình
2. Chỉ sử dụng thông tin từ database trên
3. Nếu không có thông tin, nói "Hiện chưa có thông tin về sản phẩm này"
4. Gợi ý sản phẩm liên quan khi phù hợp
5. Luôn đề cập đến giá và tình trạng tồn kho

=== CÂU HỎI ===
{user_query}

=== PHẢN HỒI ===
"""
        return prompt
    
    def format_price(self, product):
        """Định dạng thông tin giá (Không thay đổi)"""
        if product['sale_price'] and product['sale_price'] < product['price']:
            return f"{self.format_currency(product['sale_price'])} (Khuyến mãi từ {self.format_currency(product['price'])})"
        else:
            return self.format_currency(product['price'])
    
    def format_currency(self, amount):
        """Định dạng tiền tệ (Không thay đổi)"""
        return f"{int(amount):,} VNĐ"
    
    def call_ollama(self, prompt):
        """Gọi Ollama API (Không thay đổi)"""
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_k": 40,
                        "top_p": 0.9
                    }
                },
                timeout=45
            )
            if response.status_code == 200:
                return response.json().get('response', 'Xin lỗi, tôi chưa thể trả lời câu hỏi này.')
            else:
                return f"Lỗi AI (HTTP {response.status_code})"
                
        except requests.exceptions.Timeout:
            return "Xin lỗi, phản hồi đang mất nhiều thời gian. Vui lòng thử lại với câu hỏi cụ thể hơn."
        except Exception as e:
            return f"Xin lỗi, có lỗi xảy ra khi gọi AI: {str(e)}"
    
    def process_query(self, user_query):
        """Xử lý query từ người dùng (Không thay đổi)"""
        # 1. Lấy context từ database
        db_context = self.get_store_context()
        
        # 2. Tạo prompt thông minh
        prompt = self.create_smart_prompt(user_query, db_context)
        
        # 3. Gọi AI
        ai_response = self.call_ollama(prompt)
        
        # 4. Log conversation
        self.log_conversation(user_query, ai_response)
        
        context_used = {}
        if isinstance(db_context, dict):
            context_used = {
                'products_count': len(db_context.get('products', [])),
                'categories_count': len(db_context.get('categories', [])),
                'timestamp': datetime.now().isoformat()
            }

        return {
            'answer': ai_response,
            'context_used': context_used
        }
    
    def log_conversation(self, user_message, ai_response):
        """Log conversation để cải thiện AI"""
        if not self.db:
            print("Lỗi Log: Không có kết nối database.")
            return
        
        try:
            cursor = self.db.cursor()
            # Cú pháp %s của PostgreSQL giống MySQL
            cursor.execute("""
                INSERT INTO ai_conversations (user_message, ai_response, timestamp) 
                VALUES (%s, %s, NOW())
            """, (user_message[:500], ai_response[:1000])) # Giới hạn độ dài
            self.db.commit() # Quan trọng: Phải commit sau khi INSERT
            cursor.close()
        except Exception as e:
            print(f"Lỗi Log: {e}")
            self.db.rollback() # Hoàn tác nếu có lỗi

# --- Khởi tạo và API Routes ---

# Khởi tạo AI (Chỉ 1 lần)
ai_assistant = StoreAIAssistant()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Kiểm tra sức khỏe dịch vụ"""
    return jsonify({
        "status": "healthy", 
        "service": "Store AI Assistant - Level 1 (PostgreSQL)",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """API chính cho chat"""
    try:
        data = request.get_json()
        user_query = data.get('question', '').strip()
        
        if not user_query:
            return jsonify({
                "error": "Câu hỏi không được để trống",
                "example_questions": [
                    "Có những iPhone nào dưới 20 triệu?",
                    "Laptop nào đang có khuyến mãi?",
                    "Sản phẩm bán chạy nhất là gì?",
                    "Còn AirPods không?"
                ]
            }), 400
        
        # Xử lý query
        result = ai_assistant.process_query(user_query)
        
        return jsonify({
            "success": True,
            "question": user_query,
            "answer": result['answer'],
            "context": result['context_used'],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ LỖI NGHIÊM TRỌNG TRONG /api/chat: {e}")
        return jsonify({
            "error": f"Lỗi xử lý: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/store-info', methods=['GET'])
def store_info():
    """API lấy thông tin cửa hàng (cho debug)"""
    context = ai_assistant.get_store_context()
    return jsonify({
        "store_context": context,
        "timestamp": datetime.now().isoformat()
    })

# --- Chạy máy chủ ---

if __name__ == '__main__':
    # Chạy máy chủ Gunicorn (hoặc Flask dev server)
    # Render sẽ sử dụng Gunicorn (trong Start Command), không chạy qua đây
    # Dòng này chỉ dùng khi chạy local
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
