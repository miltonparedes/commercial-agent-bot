from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session

from com_agent.chat.chatbot import Chatbot
from com_agent.database.connection import get_db
from com_agent.services.twilio import TwilioService

load_dotenv()

router = APIRouter()

twilio_service = TwilioService()
chatbot = Chatbot()


@router.post("/message")
async def reply(Body: str = Form(), From: str = Form(), db: Session = Depends(get_db)):
    user_message = Body.lower()
    session_id = From

    response_message = await chatbot.process_message(user_message, session_id, db)

    twilio_service.send_message(response_message, From)
    return {"status": "message sent"}
