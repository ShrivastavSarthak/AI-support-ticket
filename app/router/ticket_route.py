from fastapi import APIRouter
from app.controller.ticket_controller import raiseTicket
from app.models.ticket_model import Ticket_model

ticket_route = APIRouter(
    prefix="/ticket",
    tags= ["Ticket"]
)


@ticket_route.post("/raise")
async def raise_ticket(ticket:Ticket_model):
    return await raiseTicket(ticket)