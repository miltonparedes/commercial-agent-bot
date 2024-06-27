from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class IntentClassifier:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.chain = self._create_chain()

    def _create_chain(self):
        prompt = ChatPromptTemplate.from_template(
            "Classify the following user input into one of these categories: "
            "1. Kavak Information, 2. Car Catalog Query, 3. Financial Query, 4. Other. "
            "User input: {user_input}"
        )
        return prompt | self.llm

    async def classify(self, user_input: str):
        response = await self.chain.ainvoke({"user_input": user_input})
        return response.content
