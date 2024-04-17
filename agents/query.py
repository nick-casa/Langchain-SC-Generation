import os


def process_query(
    input_query: str, prompt_file: str = "../prompts/sc-generation.txt"
) -> str:
    """
    Takes a user input query and processes it into a format suitable for code generation.

    :param input_query: A string representing the user query.
    :return: A processed string ready for code generation.
    """
    # Import prompt from ../promtps/sc-generation.txt
    with open(
        os.path.abspath(os.path.join(os.path.dirname(__file__), prompt_file)),
        "r",
    ) as file:
        prompt = file.read()

    # Replace {user_query} with input_query in prompt
    processed_query = prompt.replace("{user_prompt}", input_query)
    return processed_query
