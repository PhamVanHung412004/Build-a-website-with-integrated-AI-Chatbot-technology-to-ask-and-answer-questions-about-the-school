# import requests

# url = 'http://localhost:5000/chat'
# payload = {'message': 'Xin chào từ client Python!'}

# try:
#     response = requests.post(url, json=payload)
#     print("Status Code:", response.status_code)
#     print("Raw response:", response.text)  # <- kiểm tra dữ liệu thực

#     # Sau khi chắc chắn là JSON thì mới parse
#     data = response.json()
#     print("Phản hồi từ backend:", data.get("reply"))

# except requests.exceptions.JSONDecodeError:
#     print("Lỗi: Backend không trả về JSON.")
# except requests.exceptions.RequestException as e:
#     print("Lỗi kết nối:", e)
