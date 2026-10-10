from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

client = AsyncOpenAI(
    api_key = os.getenv("OPEN_AI"),
    base_url="https://openrouter.ai/api/v1"
)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

def create_chunks(pages):
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=330,
        chunk_overlap=50,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
        add_start_index=True,
    )

    document = []
    for page in pages:
        text = page["text"].strip()
        if not text:
            continue
        page_document = Document(
            page_content=text,
            metadata={
                "page": page["page"],
                "source": "upload_pdf",
            },
        )
        document.extend(splitter.split_documents([page_document]))

    return document

async def create_embedding(chunks: list[Document]):
    valid_chunks=[
        chunk for chunk in chunks
        if chunk.page_content.strip()
    ]
    
    if not valid_chunks:
        return []
    texts = [
        chunk.page_content.strip()
        for chunk in valid_chunks    
    ]
    
    response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        input= texts,
        encoding_format= "float",
        dimensions=1024
    )
    
    result = []
    
    for item in response.data:
        chunk = valid_chunks[item.index]
        result.append({
            "text": chunk.page_content.strip(),
            "metadata": chunk.metadata,
            "embedding": item.embedding
        })
    return result
