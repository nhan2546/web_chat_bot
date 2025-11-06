import requests
import json

print("🚀 BẮT ĐẦU TEST AI SERVER")
print("=" * 40)

# Test 1: Health Check
print("1. HEALTH CHECK:")
try:
    response = requests.get("http://localhost:5000/api/health")
    print(f"   Status Code: {response.status_code}")
    data = response.json()
    print(f"   Status: {data['status']}")
    print(f"   Service: {data['service']}")
    print("   ✅ HEALTH CHECK THÀNH CÔNG")
except Exception as e:
    print(f"   ❌ HEALTH CHECK THẤT BẠI: {e}")

print("\n2. CHAT TESTS:")
print("-" * 30)

# Test questions
test_questions = [
    "Hello",
    "Xin chao",
    "iPhone",
    "Laptop",
    "San pham"
]

for i, question in enumerate(test_questions, 1):
    print(f"\n   Test {i}: '{question}'")
    
    try:
        response = requests.post(
            "http://localhost:5000/api/chat",
            json={"question": question},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"      ✅ THÀNH CÔNG")
                print(f"      💬 {data['answer']}")
            else:
                print(f"      ❌ LỖI: {data.get('error', 'Unknown error')}")
        else:
            print(f"      ⚠️ HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("      🔴 LỖI KẾT NỐI: Server không phản hồi")
    except Exception as e:
        print(f"      🔴 LỖI: {e}")

print("\n" + "=" * 40)
print("🎯 TEST HOÀN TẤT")
