import argparse
from typing import List, Dict, Union
from agents import (
    process_query,
    generate_code_versions,
    generate_code_version,
    select_optimal_code,
    check_code,
    deploy_code,
    setup_environment,
)


# Set up argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a query for code generation.")
    parser.add_argument(
        "-p", "--prompt", type=str, help="The prompt for generating code", required=True
    )
    return parser.parse_args()


def main() -> None:
    """
    Main function that orchestrates the query processing, code generation, merging, checking, and deployment.
    Accepts a prompt via a command-line argument.
    """
    args = parse_arguments()
    prompt = args.prompt  # The prompt passed by command-line flag

    # First iteration
    processed_query = process_query(prompt)

    # generated_codes = generate_code_versions(processed_query) # This function generates multiple versions of code
    generated_code = generate_code_version(
        processed_query
    )  # For now, let's confine this to only one
    # optimal_code = select_optimal_code(generated_codes) # Accordingly, we won't need this for now

    check_results = check_code(
        generated_code
    )  # Check that the generated code can compile

    if check_results["status"] == "Success":
        setup_environment()
        deploy_code(generated_code)
    else:
        print("Code check failed:", check_results["errors"])


# Run the main function if this file is executed as a script
if __name__ == "__main__":
    main()
