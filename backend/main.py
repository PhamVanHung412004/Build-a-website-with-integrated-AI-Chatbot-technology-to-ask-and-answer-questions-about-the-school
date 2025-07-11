from flask import Flask, request, jsonify
from dataclasses import dataclass
from flask_cors import CORS
import torch
from typing import (
    Dict
)

from RAG import (
    VectorDB_Manager,
    Answer_Question_From_Documents,
    Sematic_Search
)

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from dataclasses import dataclass

app = Flask(__name__)
CORS(app)

@dataclass
class INIT_INFORMATION_VECTORDB:
    device_type : str = "cuda" if torch.cuda.is_available() else "cpu"
    embed_model : HuggingFaceEmbedding = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5", device=device_type)
    vectorDB = VectorDB_Manager(embed_model, device_type)
    index = vectorDB.load_index("VectorDB")
    retriever = index.as_retriever(similarity_top_k=1)

@app.route('/chat', methods=['POST'])
def chat():
    data : Dict[str, str] = request.get_json()
    message : str = data.get('message', '')
    get_context : str = Sematic_Search(message).run(INIT_INFORMATION_VECTORDB.retriever)
    result : str = Answer_Question_From_Documents(message,get_context).run()
    return jsonify({"response": result})

if __name__ == '__main__':
    # Bật chế độ debug để tự động reload khi có thay đổi code
    app.run(
        host='0.0.0.0',  # Cho phép truy cập từ bên ngoài
        port=5000,
        debug=True,      # Bật chế độ debug và auto-reload
        use_reloader=True,  # Đảm bảo reloader được bật
        threaded=True    # Cho phép xử lý nhiều request đồng thời
    )