import os 
from dotenv import load_dotenv
from pinecone import Pinecone
from app.services.rag_service import re_ranker
load_dotenv()

pc = Pinecone(
api_key= os.getenv("PINECONE_API")
)

index_name = os.getenv("PINECONE_INDEX_NAME")
index = pc.Index(index_name)

def store_embeddings(
    embedded_chunks: list[dict],
    document_id:str
):
    vectors =[]
    
    for i, chunk in enumerate(embedded_chunks):
        metadata = chunk.get("metadata") or {}
        clean_metadata = {
            key: value
            for key, value in metadata.items()
            if isinstance(value,(str,int,float,bool))
            and value is not None 
        }
        
        clean_metadata['text'] = chunk["text"]
        clean_metadata["document_id"] = document_id
        clean_metadata["chunk_index"] = i
        
        vectors.append({
            "id": f"{document_id}-{i}",
            "values": chunk["embedding"],
            "metadata": clean_metadata
        })
        
    batch_size =100
    for start in range(0, len(vectors), batch_size):
        batch = vectors[start:start+batch_size]
        
        index.upsert(
            vectors=batch,
            namespace="support_document"
        )
    
    return{
        "document_id": document_id,
        "total_stored": len(vectors)
    }


def find_query(query: list[float], rerank_query: str) -> list[dict]:
    response = index.query(
        vector=query,
        top_k=10,
        namespace="support_document",
        include_metadata=True
    )
    
    matches =[]
    
    for match in response.matches:
        matches.append({
            "text":match.metadata.get("text",""),
            "score":match.score,
            "metadata":match.metadata
        })
    final_response = re_ranker(rerank_query, matches, 5)
    return final_response