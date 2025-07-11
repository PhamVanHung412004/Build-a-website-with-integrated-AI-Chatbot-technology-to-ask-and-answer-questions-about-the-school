import requests
from typing import (
    Dict
)
while(True):
    url : str = 'http://localhost:5000/chat'

    user_query : str = input("Câu hỏi: ")
    payload : Dict[str, str]  = {'message': user_query}

    try:
        response : Dict[str, str] = requests.post(url, json=payload)

        # Sau khi chắc chắn là JSON thì mới parse
        data = response.json()
        print("-" * 50)
        print("Câu trả lời: ", data.get("response"))
        print("-" * 50)
    except requests.exceptions.JSONDecodeError:
        print("Lỗi: Backend không trả về JSON.")
    except requests.exceptions.RequestException as e:
        print("Lỗi kết nối:", e)
