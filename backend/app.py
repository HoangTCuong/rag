from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import os
import chromadb
from chromadb.config import Settings
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import pdfplumber
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.llms import CTransformers
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel


# Khởi tạo ChromaDB với chế độ persistent
chroma_client = chromadb.PersistentClient(path="./chroma_storage")

# Tạo collection nếu chưa có
collection_name = "pdf_document"
collection = chroma_client.get_or_create_collection(name = collection_name)

#khởi tạo model embedding - miễn phí
embedder = SentenceTransformer("all-MiniLM-L6-v2")

#Cau hinh model
model_file = "model/vinallama-7b-chat_q5_0.gguf"

def load_llm(model_file):
    CTransformers(
        model = model_file

    )

template = """
    <|im_start|>system
    Bạn là trợ lý AI chính xác và trung thực. 
    Chỉ dùng thông tin trong {context} để trả lời. 
    Nếu không đủ dữ liệu, hãy nói: "Tôi không có đủ thông tin để trả lời câu hỏi này."
    Không suy đoán hay bịa đặt. 
    Trả lời ngắn gọn, rõ ràng, bằng ngôn ngữ tự nhiên, trình bày khoa học.
    <|im_end|>
    <|im_start|>user
    {question}
    <|im_end|>
    <|im_start|>assistant
"""

# Chuan bi tao chain
prompt = PromptTemplate(template=template, input_variables=["context", "question"])
parser = StrOutputParser()
llm = CTransformers(model=model_file, model_type="llama", max_new_token=1024, temperature=0.1)

chain = prompt | llm | parser

class ChatRequest(BaseModel):
    question: str

# Khởi tạo FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # hoặc ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#API CHAT
@app.post("/chat")
async def chat(data: ChatRequest):
    try:
        # Tạo embedding cho câu hỏi
        query_embedding = embedder.encode(data.question).tolist()

        # Truy vấn các đoạn văn bản tương đồng nhất
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=10
        )

        # Ghép các document thành context
        documents = results["documents"][0] if results["documents"] else []
        context = "\n".join(documents)

        # Gọi model
        answer = chain.invoke({
            "question": data.question,
            "context": context
        })

        # Trả về kết quả
        return {
            "question": data.question,
            "answer": answer,
            "context_used": context,
            "sources": results["metadatas"][0] if "metadatas" in results else []
        }

    except Exception as e:
        return {"error": str(e)}


#UPLOAD TAI LIEU
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file PDF")

    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    chunks = []
    try:
        with pdfplumber.open(temp_path) as pdf:
            for page in pdf.pages:
                lines = page.extract_text().splitlines()
                for line in lines:
                    cleaned = line.strip()
                    if cleaned:
                        chunks.append(cleaned)
    except Exception as e:
        os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Lỗi đọc PDF: {str(e)}")

    os.remove(temp_path)

    if not chunks:
        raise HTTPException(status_code=400, detail="Không thể trích xuất nội dung từ PDF")

    for i, chunk in enumerate(chunks):
        embedding = embedder.encode(chunk).tolist()
        chunk_id = f"{file.filename}_line_{i}"
        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[chunk_id],
            metadatas=[{"filename": file.filename, "line_index": i}]
        )

    return JSONResponse(content={
        "message": f"Tải lên và lưu thành công {len(chunks)} dòng",
        "filename": file.filename,
        "lines": len(chunks)
    })

#LIET KE DANH SACH TAI LIEU
@app.get("/list")
def list_documents():
    results = collection.get()
    return {"ids": results["ids"], "metadatas": results["metadatas"]}


# TAO CONTEXT CHO llm
# @app.get("/search")
# def search(query: str):
#     query_embedding = embedder.encode(query).tolist()
#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=10
#     )
#     return {
#         "matches": [
#             {
#                 "id": results["ids"][i],
#                 "document": results["documents"][i],
#                 "metadata": results["metadatas"][i],
#                 "distance": results["distances"][i]
#             }
#             for i in range(len(results["ids"]))
#         ]
#     }



