import argparse
from typing import List, Dict, Union
from agents import (
    process_query,
    generate_code_version_with_feedback,
    generate_initial_code_version,
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

    # Add more arguments as needed
    # parser.add_argument("-o", "--output", type=str, help="The output file path")
    # parser.add_argument("-t", "--temperature", type=float, help="The temperature for code generation")
    # parser.add_argument("-n", "--num_versions", type=int, help="The number of code versions to generate")
    # parser.add_argument("-m", "--max_retries", type=int, help="The maximum number of retries for code generation")
    return parser.parse_args()


def main() -> None:
    """
    Main function that orchestrates the query processing,
    code generation, merging, checking, and deployment.
    Accepts a prompt via a command-line argument via -p or --prompt flag.
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
        # This function generates multiple versions of code
        # generated_codes = generate_code_versions(processed_query)
        # For now, let's confine this to only one
        if generated_code:
            generated_code = generate_code_version_with_feedback(
                processed_query, generated_code, feedback=feedback
            )
        else:
            generated_code = generate_initial_code_version(processed_query)
        # Accordingly, we won't need this for now
        # optimal_code = select_optimal_code(generated_codes)
        # Check that the generated code can compile
        check_results = check_code(generated_code)
        # Add check results to feedback
        feedback["check_results"] = check_results

        if check_results["status"] == "Success":
            print("Generated code can compile!")
            setup_environment()
            deploy_results = deploy_code(generated_code)
            # Add deployment results to feedback
            feedback["deploy_results"] = deploy_results

            if deploy_results["status"] == "Success":
                print("Generated code deployed successfully!")
                test_results = test_deployed_contract(
                    deploy_results["contract_address"]
                )
                # Add test results to feedback
                feedback["test_results"] = test_results

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
