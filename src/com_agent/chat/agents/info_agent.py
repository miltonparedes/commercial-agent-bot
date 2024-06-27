from langchain.schema.runnable import RunnablePassthrough
from langchain_community.vectorstores import PGVector
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from com_agent.config import settings


class InfoAgent:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.retriever = self._create_retriever()
        self.chain = self._create_chain()

    def _create_retriever(self):
        embeddings = OpenAIEmbeddings()
        vectorstore = PGVector(
            connection_string=settings.DATABASE_URL,
            embedding_function=embeddings,
            collection_name="company_info",
        )
        return vectorstore.as_retriever()

    def _create_chain(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Eres un asistente útil que proporciona información sobre Kavak. Utiliza la siguiente información relevante para responder a las consultas del usuario.",
                ),
                ("human", "Información relevante: {context}"),
                ("human", "Pregunta del usuario: {question}"),
                (
                    "human",
                    "Responde a la pregunta basándote en la información proporcionada arriba.",
                ),
            ]
        )

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        return rag_chain

    async def process(self, query: str):
        return await self.chain.ainvoke(query)
