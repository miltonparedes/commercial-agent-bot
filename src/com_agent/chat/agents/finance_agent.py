from typing import Any, Dict, List

from langchain.agents import AgentExecutor, Tool, create_openai_functions_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage, HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI


class FinanceInput(BaseModel):
    car_price: float = Field(description="Price of the car in Mexican pesos")
    down_payment: float = Field(description="Down payment amount in Mexican pesos")
    term: int = Field(description="Financing term in years (between 3 and 6)")


def calculate_financing(input_str: str) -> str:
    inputs = eval(input_str)
    car_price = inputs["car_price"]
    down_payment = inputs["down_payment"]
    term = inputs["term"]

    if term < 3 or term > 6:
        return "The term must be between 3 and 6 years."

    amount_to_finance = car_price - down_payment
    annual_rate = 0.10  # 10% annual rate
    monthly_rate = annual_rate / 12
    term_months = term * 12

    monthly_payment = (
        amount_to_finance * monthly_rate * (1 + monthly_rate) ** term_months
    ) / ((1 + monthly_rate) ** term_months - 1)

    return (
        f"For a car priced at ${car_price:,.2f} MXN with a down payment of ${down_payment:,.2f} MXN over {term} years:\n"
        f"- Amount to finance: ${amount_to_finance:,.2f} MXN\n"
        f"- Estimated monthly payment: ${monthly_payment:,.2f} MXN\n"
        f"- Term: {term_months} months\n"
        f"- Annual interest rate: {annual_rate*100}%"
    )


class FinanceAgent:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.memory = ConversationBufferWindowMemory(
            k=10, memory_key="chat_history", return_messages=True
        )
        self.agent_executor = self._create_agent()

    def _create_agent(self) -> AgentExecutor:
        finance_tool = Tool(
            name="FinancingCalculator",
            func=calculate_financing,
            description="Calculates the financing plan. Input: a dictionary with 'car_price', 'down_payment', and 'term' in years (3-6).",
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a Kavak financial assistant helping customers with car financing plans. "
                    "Use the Financing Calculator to provide accurate details about the plans.",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_openai_functions_agent(self.llm, [finance_tool], prompt)
        return AgentExecutor(
            agent=agent, tools=[finance_tool], verbose=True, memory=self.memory
        )

    async def process(
        self, query: str, chat_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        formatted_history = []
        for message in chat_history:
            if message["type"] == "human":
                formatted_history.append(HumanMessage(content=message["content"]))
            elif message["type"] == "ai":
                formatted_history.append(AIMessage(content=message["content"]))

        self.memory.chat_memory.messages = formatted_history

        return await self.agent_executor.ainvoke(
            {"input": query, "chat_history": formatted_history}
        )
