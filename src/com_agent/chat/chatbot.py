from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session

from com_agent.chat.agents.catalog_agent import CatalogAgent
from com_agent.chat.agents.finance_agent import FinanceAgent
from com_agent.chat.agents.info_agent import InfoAgent
from com_agent.chat.intent_classifier import IntentClassifier
from com_agent.config import settings


class Chatbot:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0,
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )
        self.intent_classifier = IntentClassifier(self.llm)
        self.info_agent = InfoAgent(self.llm)
        self.catalog_agent = CatalogAgent(self.llm)
        self.finance_agent = FinanceAgent(self.llm)
        self.response_interpreter = self._create_response_interpreter()

    def _create_response_interpreter(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Eres un asistente amable y profesional de Kavak. Tu tarea es interpretar y reformular la información proporcionada por nuestros agentes especializados para ofrecer una respuesta coherente y natural al cliente.",
                ),
                ("human", "Entrada del usuario: {user_input}"),
                ("human", "Respuesta del agente especializado: {agent_response}"),
                (
                    "human",
                    "Por favor, interpreta esta información y proporciona una respuesta amigable y natural al cliente, manteniendo la esencia de la información proporcionada por el agente especializado.",
                ),
            ]
        )
        return prompt | self.llm | StrOutputParser()

    async def process_message(self, user_message: str, session_id: str, db: Session):
        history = SQLChatMessageHistory(
            session_id=session_id, connection_string=settings.DATABASE_URL
        )
        history.add_user_message(user_message)

        intent = await self.intent_classifier.classify(user_message)

        chat_history = history.messages[-5:]

        if "Financial Query" in intent:
            agent_response = await self.finance_agent.process(
                user_message,
                [{"type": msg.type, "content": msg.content} for msg in chat_history],
            )
        elif "Kavak Information" in intent:
            agent_response = await self.info_agent.process(user_message)
        elif "Car Catalog Query" in intent:
            agent_response = await self.catalog_agent.process(user_message)
        else:
            agent_response = "No estoy seguro de cómo responder a eso. ¿Puedes ser más específico sobre si necesitas información de Kavak, detalles del catálogo o ayuda con financiamiento?"

        if isinstance(agent_response, dict):
            agent_response = agent_response.get("output", str(agent_response))

        interpreted_response = await self.response_interpreter.ainvoke(
            {"user_input": user_message, "agent_response": agent_response}
        )

        history.add_ai_message(interpreted_response)
        return interpreted_response
