# Tệp: AI_SEVER/app.py

# --- PHẦN IMPORT (ĐẦU TỆP) ---
import os 
# import psycopg2 # <-- XÓA DÒNG NÀY
# import psycopg2.extras # <-- XÓA DÒNG NÀY
import mysql.connector # <-- THÊM DÒNG NÀY
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime

# ...

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


# --- PHẦN CLASS (HÀM KẾT NỐI) ---
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
            return mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT
            )
        except Exception as e:
            print(f"❌ Lỗi kết nối Database Railway: {e}")
            return None

    def get_store_context(self):
        """Lấy toàn bộ context cửa hàng cho AI"""
        if not self.db:
            return "Không thể kết nối database"
        
        try:
            # Dùng 'dictionary=True' cho mysql-connector
            cursor = self.db.cursor(dictionary=True)
            
            # ... (Phần còn lại của hàm get_store_context của bạn) ...
