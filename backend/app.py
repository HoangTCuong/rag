# app.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import os
import chromadb
from chromadb.config import Settings
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
import pdfplumber
import torch

# Khởi tạo ChromaDB với chế độ persistent
chroma_client = chromadb.PersistentClient(path="./chroma_storage")

# Tạo collection nếu chưa có
collection_name = "pdf_document"
collection = chroma_client.get_or_create_collection(name = collection_name)

#khởi tạo model embedding - miễn phí
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Khởi tạo FastAPI
app = FastAPI()


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

@app.get("/list")
def list_documents():
    results = collection.get()
    return {"ids": results["ids"], "metadatas": results["metadatas"]}

@app.get("/search")
def search(query: str):
    query_embedding = embedder.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=4
    )
    return {
        "matches": [
            {
                "id": results["ids"][i],
                "document": results["documents"][i],
                "metadata": results["metadatas"][i],
                "distance": results["distances"][i]
            }
            for i in range(len(results["ids"]))
        ]
    }

# # System prompt
# SYSTEM_PROMPT = (
#     "based on the information you have in the file, answer the question by them, "
#     "if you dont have information tell the user you don't know, use the same language with question from the user"
# )

# # Load model từ Hugging Face (miễn phí, chạy local)
# model_name = "mistralai/Mistral-7B-Instruct-v0.2"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")

# @app.get("/ask")
# def ask(query: str = Query(..., description="Câu hỏi của người dùng")):
#     # Truy vấn ChromaDB
#     query_embedding = embedder.encode(query).tolist()
#     results = collection.query(query_embeddings=[query_embedding], n_results=5)

#     # Ghép các đoạn văn bản liên quan
#     context = "\n".join(results["documents"])

#     # Tạo prompt cho LLM
#     full_prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion:\n{query}"

#     # Tokenize và sinh câu trả lời
#     inputs = tokenizer(full_prompt, return_tensors="pt").to(model.device)
#     output = model.generate(
#         **inputs,
#         max_new_tokens=512,
#         do_sample=True,
#         temperature=0.7,
#         top_p=0.9
#     )
#     answer = tokenizer.decode(output[0], skip_special_tokens=True)

#     # Cắt bỏ phần prompt nếu model lặp lại
#     if "Question:" in answer:
#         answer = answer.split("Question:")[-1].strip()

#     return JSONResponse(content={"answer": answer})


