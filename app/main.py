from fastapi import FastAPI
from app.router.ticket_route import ticket_route
from app.router.upload_route import upload_route

app = FastAPI(
    title="AI Support Ticket",
    version="1.0.0"
)

app.include_router(ticket_route)
app.include_router(upload_route)

@app.get("/")
async def root():
    return{
        "message":"AI-support-ticket API is running"
    }