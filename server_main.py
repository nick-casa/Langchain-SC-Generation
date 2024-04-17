from flask import Flask, request, jsonify
import subprocess
import os
from dotenv import load_dotenv
from agents import process_query, SmartContractGenerator, check_code, deploy_contract

app = Flask(__name__)
# Start Ganache CLI as a subprocess
ganache_process = subprocess.Popen(
    ["ganache-cli", "-p", "8545"], stdout=subprocess.PIPE
)
load_dotenv()

generator = SmartContractGenerator(
    azure_config=None, model_name="gpt-3.5-turbo", temperature=0.6
)


@app.route("/")
def index():
    return "Ganache CLI running in background on port 7545"


@app.route("/shutdown", methods=["POST"])
def shutdown():
    ganache_process.terminate()
    return "Ganache CLI terminated"


@app.route("/process", methods=["POST"])
def process_code():
    data = request.json
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    valid_output = False
    generated_code, check_results, deploy_results = None, None, None
    max_retries = 5
    attempt_count = 0
    feedback = {}

    while not valid_output and attempt_count < max_retries:
        attempt_count += 1
        processed_query = process_query(
            prompt, prompt_file="../prompts/sc-generation-2.txt"
        )
        generated_code = generator.generate_initial_code_version(processed_query)

        check_results = check_code(generated_code)
        feedback["check_results"] = check_results

        if check_results["status"] == "Success":
            deploy_results = deploy_contract(generated_code)
            feedback["deploy_results"] = deploy_results

            if deploy_results["status"] == "Success":
                valid_output = True

    if not valid_output:
        return jsonify({"error": "Failed to deploy code successfully"}), 500

    return jsonify(
        {
            "generated_code": generated_code,
            "check_results": check_results,
            "deploy_results": deploy_results,
        }
    )


if __name__ == "__main__":
    try:
        app.run(port=5000, debug=True)
    finally:
        # Ensure Ganache CLI is terminated when Flask app stops
        ganache_process.terminate()
