# Tệp: AI_SEVER/app.py
# Phiên bản cuối cùng: Đã nâng cấp để sử dụng MySQL (Railway)

# --- PHẦN IMPORT (ĐẦU TỆP) ---
import os 
import mysql.connector # <-- Thư viện MySQL
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime

# --- PHẦN CONFIG ---
app = Flask(__name__)
CORS(app)

# Lấy URL của Ollama
OLLAMA_URL = os.getenv('OLLAMA_HOST', 'http://ollama:11434')

# Lấy 5 biến MySQL (Railway) từ Render
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT', 3306) # Mặc định là 3306 nếu không tìm thấy

print("🚀 AI SERVER ĐANG KHỞI ĐỘNG...")
if not DB_HOST:
    print("❌ LỖI NGHIÊM TRỌNG: Biến môi trường 'DB_HOST' chưa được cài đặt.")
else:
    print(f"ℹ️ Đang cố gắng kết nối đến Host: {DB_HOST}:{DB_PORT} với User: {DB_USER}")


# --- LỚP AI CHÍNH ---

class StoreAIAssistant:
    def __init__(self):
        self.db = self.connect_db()
        if self.db:
            print("✅ Đã kết nối thành công đến Railway (MySQL)!")
        
    def connect_db(self):
        """Kết nối đến database MySQL (Railway)"""
        if not DB_HOST:
            print("❌ Lỗi kết nối: Các biến môi trường DB chưa được cài đặt.")
            return None
        try:
            # Sử dụng 5 biến để kết nối mysql.connector
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT,
                connect_timeout=10
            )
            return conn
        except Exception as e:
            # Ghi lại lỗi đầy đủ vào Logs của Render
            print(f"❌ Lỗi kết nối Database Railway nghiêm trọng: {e}")
            return None
    
    def get_store_context(self):
        """Lấy toàn bộ context cửa hàng cho AI"""
        if not self.db or not self.db.is_connected():
            print("⚠️ Mất kết nối DB, đang thử kết nối lại...")
            self.db = self.connect_db() # Thử kết nối lại
            if not self.db:
                return "Không thể kết nối database"
        
        try:
            # Dùng 'dictionary=True' cho mysql-connector
            cursor = self.db.cursor(dictionary=True)
            
            # Lấy sản phẩm với categories
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
            print(f"❌ Lỗi khi đang lấy dữ liệu (get_store_context): {e}")
            return f"Lỗi lấy dữ liệu: {str(e)}"
    
    def create_smart_prompt(self, user_query, db_context):
        """Tạo prompt thông minh cho AI"""
        
        # Kiểm tra nếu db_context là một chuỗi lỗi
        if isinstance(db_context, str):
            print(f"⚠️ Không thể tạo prompt, lỗi context: {db_context}")
            return f"Tôi không thể lấy thông tin cửa hàng: {db_context}. Vui lòng thử lại sau."

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
        """Định dạng thông tin giá"""
        if product['sale_price'] and product['sale_price'] < product['price']:
            return f"{self.format_currency(product['sale_price'])} (Khuyến mãi từ {self.format_currency(product['price'])})"
        else:
            return self.format_currency(product['price'])
    
    def format_currency(self, amount):
        """Định dạng tiền tệ"""
        return f"{int(amount):,} VNĐ"
    
    def call_ollama(self, prompt):
        """Gọi Ollama API"""
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
            response.raise_for_status() # Báo lỗi nếu HTTP code là 4xx hoặc 5xx
            return response.json().get('response', 'Xin lỗi, tôi chưa thể trả lời câu hỏi này.')
                
        except requests.exceptions.Timeout:
            print("❌ Lỗi AI: Ollama timeout")
            return "Xin lỗi, phản hồi đang mất nhiều thời gian. Vui lòng thử lại với câu hỏi cụ thể hơn."
        except Exception as e:
            print(f"❌ Lỗi AI: Không thể gọi Ollama: {e}")
            return f"Xin lỗi, có lỗi xảy ra khi gọi AI: {str(e)}"
    
    def process_query(self, user_query):
        """Xử lý query từ người dùng"""
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
        if not self.db or not self.db.is_connected():
            print("Lỗi Log: Không có kết nối database.")
            return
        
        try:
            cursor = self.db.cursor()
            # Cú pháp %s của MySQL giống PostgreSQL
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
        "service": "Store AI Assistant - Level 1 (MySQL/Railway)",
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
    # Render sẽ sử dụng Gunicorn (trong Start Command), không chạy qua đây
    # Dòng này chỉ dùng khi chạy local
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
