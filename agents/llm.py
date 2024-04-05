from typing import List, Dict, Union
from typing_extensions import Protocol
import os

# from langchain.llms.openai import AzureOpenAI, OpenAI
from langchain_community.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


class SmartContractGenerator:
    def __init__(
        self,
        azure_config: Dict[str, str] = None,
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

    def generate_initial_code_version(self, processed_prompt: str) -> str:
        """
        Generates the initial version of code based on the given processed query.

        Args:
            processed_prompt (str): The processed query string intended for code generation.

        Returns:
            str: The initially generated code as a string.
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

    def generate_code_version_with_feedback(
        self,
        processed_prompt: str,
        output_code: str,
        feedback: Dict[str, Union[str, List[str]]] = None,
    ) -> str:
        """
        Enhances the code generation process by utilizing feedback from previous attempts to generate a refined version of code.

        Args:
            processed_prompt (str): The processed query string for which the code is generated.
            output_code (str): The output code from the previous code generation attempt.
            feedback (Dict[str, Union[str, List[str]]], optional): Feedback provided from previous checks, deployments, or tests, structured as a dictionary. This feedback includes keys such as 'check_results', 'deploy_results', and 'test_results', each possibly containing a sub-dictionary with an 'errors' key that maps to a string or list of strings detailing specific issues.

        Returns:
            str: The newly generated code as a string, taking into account the provided feedback.
        """
        messages = [
            SystemMessage(content=processed_prompt),
            HumanMessage(
                content="Here is the code generated from the previous attempt:"
            ),
            HumanMessage(content=output_code),
        ]

        if "check_results" in feedback and feedback["check_results"]:
            messages.append(
                HumanMessage(
                    content="The generated code failed to compile. Here is the associated error(s):"
                )
            )
            messages.append(HumanMessage(content=feedback["check_results"]["errors"]))

        if "deploy_results" in feedback and feedback["deploy_results"]:
            messages.append(
                HumanMessage(
                    content="The generated code failed to deploy. Here is the associated error(s):"
                )
            )
            messages.append(HumanMessage(content=feedback["deploy_results"]["errors"]))

        if "test_results" in feedback and feedback["test_results"]:
            messages.append(
                HumanMessage(
                    content="The deployed contract failed the security tests. Here is the associated error(s):"
                )
            )
            messages.append(HumanMessage(content=feedback["test_results"]["errors"]))

        messages.append(
            SystemMessage(
                content="Utilize the feedback to enhance the code. Pay attention to the errors and warnings. Output only the code."
            )
        )
        # Implement logic to modify code generation based on feedback
        print(
            f"\033[94m************** Generating Smart Contract (With Feedback) With LLM ************** \033[0m"
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
