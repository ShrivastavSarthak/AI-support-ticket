from app.services.rag_service import create_chunks, create_embedding
from app.services.pinecone_service import store_embeddings
from fastapi import HTTPException, UploadFile
import fitz

async def uploadFile(file: UploadFile,fileName:str):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail= "Only PDF is allowed"
        )
    pages = []

    file_bytes = await file.read()
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
        for page_number, page in enumerate(pdf,start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append({
                    "page":page_number,
                    "text":text
                })
    chunks = create_chunks(pages)
    embeddings = await create_embedding(chunks)
    result = store_embeddings(
        embeddings,
        document_id=fileName
    )
    return{
        "message":"PDF embedding stored successfully",
        "result":result
    }