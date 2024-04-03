from typing import List, Dict, Union
from typing_extensions import Protocol

# from langchain.llms.openai import AzureOpenAI, OpenAI
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


class SmartContractGenerator:
    def __init__(
        self,
        azure_config: Dict[str, str] | None,
        model_name: str = "gpt-3.5-turbo-0125",
        temperature: float = 0.5,
        request_timout: int = 120,
    ):
        if not azure_config and not os.environ["OPENAI_API_KEY"]:
            raise ValueError("Azure Config or OpenAI API key are missing.")

        if azure_config:
            self.llm = AzureChatOpenAI(
                openai_api_type="azure",
                openai_api_base=azure_config["openai_api_base"],
                openai_api_key=azure_config["openai_api_key"],
                openai_api_version="2023-05-15",
                deployment_name=azure_config["deployment_name"],
                model_name=model_name,
                temperature=temperature,
                request_timeout=request_timout,
            )
        else:
            self.llm = ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                request_timeout=request_timout,
            )
        print(
            f"\033[94m************** LLM Smart Contract Generator Successfully Initialized ************** \033[0m"
        )

    def generate_code_version(
        self, processed_prompt: str, feedback: Dict[str, Union[str, List[str]]] = None
    ) -> str:
        """
        Generates a version of code from the processed query, optionally using feedback from previous attempts.

        :param processed_prompt: The user processed query string.
        :param feedback: A dictionary containing feedback from previous code checks, deployments, or tests.
        :return: Generated code as a string.
        """
        messages = [
            SystemMessage(content=processed_prompt),
        ]
        # Implement logic to modify code generation based on feedback
        print(
            f"\033[94m************** Generating Smart Contract With LLM ************** \033[0m"
        )
        response = self.llm(messages).content
        return response


if __name__ == "__main__":
    # import environment variables
    from dotenv import load_dotenv
    import os

    from query import process_query

    # Load environment variables from parent folder
    dot_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
    load_dotenv(dot_env_path)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = openai_api_key

    user_prompt = "Generate a smart contract for a simple voting system."
    processed_prompt = process_query(user_prompt)

    generator = SmartContractGenerator(azure_config=None)
    generated_code = generator.generate_code_version(processed_prompt)
    print(generated_code)
