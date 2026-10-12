from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from openai import AsyncOpenAI
from dotenv import load_dotenv
import cohere
import os
load_dotenv()

client = AsyncOpenAI(
    api_key = os.getenv("OPEN_AI"),
    base_url="https://openrouter.ai/api/v1"
)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
CHAT_MODEL = "openrouter/free"

def create_chunks(pages):
    combine_text = ""
    for page in pages:
        page_text = page.get("text","")
        page_num = page.get("page",1)
        if isinstance(page_text,list):
            text = "\n".join([str(item).strip() for item in page_text if item])
        else:
            text = str(page_text).strip()
        if text:
            combine_text += f"\n\n[Page {page_num}]" +text
    
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=700,
        chunk_overlap=100,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
        add_start_index=True,
    )

    master_doc = Document(
        page_content= combine_text,
        metadata = {"source": "upload_pdf"}
    )
    chunk = splitter.split_documents([master_doc])
    return chunk

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

async def llm_response(ans_chunk: list[dict], question: str):
    context = "\n\n".join(
        chunk["text"] for chunk in ans_chunk
        if chunk.get("text")
    )

    instructions = f"""
You are an AI customer support assistant for our e-commerce company.

Answer the customer using ONLY the company information provided below.

If the answer is not available in the provided information, say:
"I don't have that information in the company documents."

COMPANY INFORMATION:
{context}
"""

    response = await client.responses.create(
        model=CHAT_MODEL,
        instructions=instructions,
        input=question,
        temperature=0.5
    )

    return response.output_text

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def re_ranker(query, chunk, top_k_final=3):
    
    retrieved_doc=chunk
    if not retrieved_doc:
        return []
    documents_to_re_rank = [doc['text'] for doc in retrieved_doc]
    rerank_response = co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=documents_to_re_rank,
        top_n=top_k_final
    )
    final_chunk = []
    
    for result in rerank_response.results:
        original_doc = retrieved_doc[result.index]
        original_doc["relevance_score"] = result.relevance_score
        final_chunk.append(original_doc)
    return final_chunk