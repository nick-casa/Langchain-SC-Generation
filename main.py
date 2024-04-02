import argparse
from typing import List, Dict, Union
from agents import (
    process_query,
    generate_code_versions,
    generate_code_version,
    select_optimal_code,
    check_code,
    deploy_code,
    test_deployed_contract,
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
    prompt = args.prompt
    valid_output = False
    max_retries = 5
    attempt_count = 0
    feedback = {}

    while not valid_output and attempt_count < max_retries:
        attempt_count += 1
        print(f"Attempt {attempt_count} of {max_retries}")

        processed_query = process_query(prompt)
        # generated_codes = generate_code_versions(processed_query) # This function generates multiple versions of code
        generated_code = generate_code_version(
            processed_query, feedback=feedback
        )  # For now, let's confine this to only one
        # optimal_code = select_optimal_code(generated_codes) # Accordingly, we won't need this for now
        check_results = check_code(
            generated_code
        )  # Check that the generated code can compile
        feedback["check_results"] = check_results  # Add check results to feedback

        if check_results["status"] == "Success":
            print("Generated code can compile!")
            setup_environment()
            deploy_results = deploy_code(generated_code)
            feedback["deploy_results"] = (
                deploy_results  # Add deployment results to feedback
            )

            if deploy_results["status"] == "Success":
                print("Generated code deployed successfully!")
                test_results = test_deployed_contract(
                    deploy_results["contract_address"]
                )
                feedback["test_results"] = test_results  # Add test results to feedback

                if test_results["status"] == "Pass":
                    print("Deployed contract tests passed:", test_results)
                    valid_output = True
                else:
                    print("Deployed contract tests failed:", test_results["errors"])
            else:
                print("Code deployment failed:", deploy_results["errors"])
        else:
            print("Code check failed:", check_results["errors"])

        if not valid_output:
            print("Operation failed, attempting again...\n")

    if not valid_output:
        print("Failed to process and deploy code successfully after maximum retries.")


if __name__ == "__main__":
    main()
