# app.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import os
import chromadb
from chromadb.config import Settings
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import pdfplumber
from fastapi.middleware.cors import CORSMiddleware


# Khởi tạo ChromaDB với chế độ persistent
chroma_client = chromadb.PersistentClient(path="./chroma_storage")

# Tạo collection nếu chưa có
collection_name = "pdf_document"
collection = chroma_client.get_or_create_collection(name = collection_name)

#khởi tạo model embedding - miễn phí
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Khởi tạo Claude client

# Khởi tạo FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # hoặc ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        n_results=10
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



