from app.models.ticket_model import Ticket,Ticket_model
from langchain_core.documents import Document
from app.services.pinecone_service import find_query
from app.services.rag_service import create_embedding, llm_response

async def raiseTicket(ticket:Ticket_model):
    newTicket = Ticket(
        title = ticket.title,
        description = ticket.description,
        category = ticket.category,
        file = ticket.file,
    )
    ticket_text = f"""
        Title:{ticket.title},
        Description:{ticket.description},
        Category:{ticket.category},
    """

    query_embedding = await create_embedding([
        Document(page_content=ticket_text)
    ])
    relevant_ans = find_query(query_embedding[0]["embedding"], ticket_text)
    
    llm_res = await llm_response(relevant_ans,ticket_text)
    return {
        "message":"ticket raised successfully",
        "response":llm_res,
    }