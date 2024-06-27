from typing import Any, Dict

import pandas as pd
from langchain.agents import AgentExecutor
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI


class CatalogAgent:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.agent_executor = self._create_agent()

    def _create_agent(self) -> AgentExecutor:
        df = pd.read_csv("com_agent/data/catalog.csv")
        return create_pandas_dataframe_agent(
            self.llm,
            df,
            verbose=True,
            agent_type="tool-calling",
            agent_executor_kwargs={"handle_parsing_errors": True},
            allow_dangerous_code=True,
        )

    async def process(self, query: str) -> Dict[str, Any]:
        try:
            result = await self.agent_executor.ainvoke({"input": query})
            return result
        except Exception as e:
            return {
                "output": f"Lo siento, hubo un error al procesar tu consulta: {str(e)}"
            }
