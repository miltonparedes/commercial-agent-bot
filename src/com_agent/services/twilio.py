from twilio.rest import Client

from com_agent.config import settings


class TwilioService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    def send_message(self, body: str, to: str):
        return self.client.messages.create(
            body=body, from_=settings.TWILIO_PHONE_NUMBER, to=to
        )
