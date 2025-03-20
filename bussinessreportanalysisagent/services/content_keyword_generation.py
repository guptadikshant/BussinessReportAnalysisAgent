from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from bussinessreportanalysisagent.application.rag.prompt_templates import KEYWORD_EXTACTION_TEMPLATE
from bussinessreportanalysisagent.models.models import LLMModel


class Keyword(BaseModel):
    newKeyword: list = Field(description="List of three keyword belongs to the Content")


class ContentKeyword:

    @staticmethod
    def get_content_keyword(keywords_list: list[str], content: str, model_name: str, model_temperature: int) -> list[str]:

        keywords = keywords_list
        parser = PydanticOutputParser(pydantic_object=Keyword)
        prompt = PromptTemplate(

            template=KEYWORD_EXTACTION_TEMPLATE,
            input_variables=["keywords", "content"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        chain = prompt | LLMModel().get_groq_model(model_name=model_name, temperature=model_temperature)  | parser
        result = chain.invoke({"keywords": keywords, "content": content})
        return result.newKeyword
