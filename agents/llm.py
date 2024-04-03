from typing import List, Dict, Union
from typing_extensions import Protocol
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms.openai import AzureOpenAI, OpenAI


class SmartContractGenerator:
    def __init__(
        self,
        template: str,
        azure_config: Dict[str, str] | None,
        openai_api_key: str | None,
        temperature: float = 0.5,
        request_timout: int = 10,
    ):
        self.prompt = PromptTemplate(input_variables=["user_prompt"], template=template)
        if not azure_config and not openai_api_key:
            raise ValueError("Either Azure config or OpenAI API key must be provided.")

        if azure_config:
            self.llm = AzureOpenAI(
                openai_api_type="azure",
                openai_api_base=azure_config["openai_api_base"],
                openai_api_key=azure_config["openai_api_key"],
                openai_api_version="2023-05-15",
                deployment_name=azure_config["deployment_name"],
                model_name=azure_config["model_name"],
                temperature=temperature,
                request_timeout=request_timout,
            )
        else:
            self.llm = OpenAI(
                openai_api_key=openai_api_key,
                temperature=temperature,
                request_timeout=request_timout,
            )
        print(self.llm)
        self.llm_chain = LLMChain(prompt=self.prompt, llm=self.llm)

    def parse_ai_message(self, message):
        print(message)

    def generate_code_version(
        self, user_prompt: str, feedback: Dict[str, Union[str, List[str]]] = None
    ) -> str:
        """
        Generates a version of code from the processed query, optionally using feedback from previous attempts.

        :param user_prompt: The user processed query string.
        :param feedback: A dictionary containing feedback from previous code checks, deployments, or tests.
        :return: Generated code as a string.
        """
        # Implement logic to modify code generation based on feedback
        response = self.llm_chain.generate(input_list=[{"user_prompt": user_prompt}])
        response = self.parse_ai_message(response)
        return response

    # TODO: Implement the following methods in the SmartContractGenerator class:
    # def generate_code_versions(prompt: str) -> List[str]:
    #     """
    #     Generates multiple versions of code from a given prompt.

    #     :param prompt: A string prompt to feed into the language model.
    #     :return: A list of generated code versions.
    #     """
    #     passa


if __name__ == "__main__":
    # import environment variables
    from dotenv import load_dotenv
    import os

    # Load environment variables from parent folder
    dot_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
    load_dotenv(dot_env_path)

    user_prompt = "Generate a smart contract for a simple voting system."

    openai_api_key = os.getenv("OPENAI_API_KEY")

    with open(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../prompts/sc-generation.txt")
        ),
        "r",
    ) as file:
        template = file.read()

    generator = SmartContractGenerator(
        template, azure_config=None, openai_api_key=openai_api_key
    )
    generator.generate_code_version(user_prompt)
