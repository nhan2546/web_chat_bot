# test_api.py - Test AI tự động
def test_full_auto():
    questions = [
        "Có iPhone nào không?",
        "MacBook giá bao nhiêu?",
        "Tôi muốn mua laptop",
        "Cập nhật giá iPhone thành 15 triệu",  # Admin feature
        "Sản phẩm nào đang hot?"
    ]
    
    for q in questions:
        response = requests.post("http://localhost:5000/api/chat", 
                               json={"question": q, "role": "admin"})
        data = response.json()
        print(f"Q: {q}")
        print(f"A: {data.get('answer')}")
        print(f"Auto: {data.get('automated', False)}")
        print("---")