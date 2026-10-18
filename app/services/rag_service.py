from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from openai import AsyncOpenAI
from dotenv import load_dotenv
import cohere
import os
from app.services.email_service import email_service
from app.tools.email_tool import EMAIL_TOOL
import json
from app.models.email_model import Email_model
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

    COMPANY INFORMATION:
    {context}

    RULES:
    1. Answer the customer using ONLY the company information provided above.
    2. If the answer is not available in the provided information, say:
       "I don't have that information in the company documents."

    3. you MUST use the `email_service` tool to send an email containing
       the details of the complaint. Do this even if the customer does
       not explicitly ask you to send an email.
    
    4. After sending the email successfully, respond to the customer in chat
       and inform them that their complaint has been noted and that the
       support team will provide them with an update.

    5. If the customer has not provided their email address, politely ask
       for their email address before sending the email. Do not claim that
       an email has been sent until the tool confirms success.

    6. Include the relevant complaint details in the email, such as the
       customer's email address, product name, complaint description,
       and return/refund issue, whenever available.

    7. Do not send duplicate emails for the same complaint within the
       same conversation unless the customer reports a new or different issue.

    8. For other questions that are not return/refund complaints, answer
       normally using the company information above.
    """

    response = await client.responses.create(
        model=CHAT_MODEL,
        instructions=instructions,
        input=question,
        temperature=0.5,
        tools=[EMAIL_TOOL],
    )
    
    for item in response.output:
        if item.type  != "function_call":
            continue
        if item.name == "email_service":
            args = json.loads(item.arguments)
            mail = Email_model(
                receiver_mail= args['receiver_mail'],
                title= args['title'],
                content= args["content"]
            )
            
            result = email_service(mail)
            
            response = await client.responses.create(
                model=CHAT_MODEL,
                instructions=instructions,
                input=[
                {
                    "role": "user",
                    "content": question
                },
                {
                    "type": "function_call",
                    "call_id": item.call_id,
                    "name": item.name,
                    "arguments": item.arguments
                },
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result)
                }
                ],
                tools=[EMAIL_TOOL]
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