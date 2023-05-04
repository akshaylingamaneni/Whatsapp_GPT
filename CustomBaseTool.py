from typing import Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    question: str = Field()

class CustomCalculatorTool(BaseTool):
    name = "Calculator"
    description = "useful for when you need to answer questions about math"
    args_schema: Type[BaseModel] = CalculatorInput

    def _run(self, query: str) -> str:
        """Use the tool."""
        return llm_math_chain.run(query)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("BingSearchRun does not support async")