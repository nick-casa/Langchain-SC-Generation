import subprocess
import tempfile
import os
import json
import re
from typing import Dict, List, Union


def get_solidity_version(code: str) -> str:
    match = re.search(r"pragma solidity\s+([^;]+);", code)
    return match.group(1).strip() if match else None


def set_solc_version(version: str) -> bool:
    try:
        version = version.replace("^", "")
        subprocess.run(
            ["solc-select", "install", version],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            ["solc-select", "use", version],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode("utf-8").strip()
        return error_message


def run_static_analyses(contract_path: str, temp_dir: str) -> List[str]:
    errors = []
    slither_output_path = os.path.join(temp_dir, "slither_output.json")
    try:
        result = subprocess.run(
            ["slither", contract_path, "--json", slither_output_path],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return [f"Slither failed to execute: {result.stderr}"]

        with open(slither_output_path, "r") as file:
            slither_output = json.load(file)

        for detector in slither_output.get("detectors", []):
            issue_description = f"{detector.get('check', 'Unknown Check')}: {detector.get('description', 'No description provided.')}"
            errors.append(issue_description)

    except Exception as e:
        errors.append(f"Error running static analysis: {str(e)}")

    return errors


def check_code(
    code: str, analysis_depth: str = "standard"
) -> Dict[str, Union[str, List[str], Dict]]:
    errors: List[str] = []
    abi: Dict = {}

    solidity_version = get_solidity_version(code)
    if solidity_version is None:
        return {
            "status": "Failure",
            "errors": ["No Solidity version specified in the pragma statement."],
        }

    version_set = set_solc_version(solidity_version)
    if version_set is not True:
        return {
            "status": "Failure",
            "errors": [
                f"Failed to set Solidity version to {solidity_version}. Ensure it is installed and try again.",
                version_set,
            ],
        }

    with tempfile.TemporaryDirectory() as temp_dir:
        contract_path = os.path.join(temp_dir, "Contract.sol")
        with open(contract_path, "w") as file:
            file.write(code)

        compile_cmd = ["solc", "--standard-json", "--allow-paths", temp_dir]
        compile_input = {
            "language": "Solidity",
            "sources": {"Contract.sol": {"content": code}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": [
                            "abi",
                            "metadata",
                            "evm.bytecode",
                            "evm.bytecode.sourceMap",
                        ]
                    }
                }
            },
        }

        try:
            compile_result = subprocess.run(
                compile_cmd,
                input=json.dumps(compile_input),
                capture_output=True,
                text=True,
                check=False,
            )
            compile_output = json.loads(compile_result.stdout)

            if "errors" in compile_output:
                for error in compile_output["errors"]:
                    if error.get("severity") in ["error", "warning"]:
                        errors.append(
                            error.get("formattedMessage", "Unknown compilation issue.")
                        )

            if compile_output.get("contracts"):
                # Iterate over all contracts in the file
                for contract_name, contract_data in compile_output["contracts"][
                    "Contract.sol"
                ].items():
                    if "abi" in contract_data:
                        abi[contract_name] = contract_data["abi"]

            if not errors or all("warning" in e for e in errors):
                analysis_errors = run_static_analyses(contract_path, temp_dir)
                errors.extend(analysis_errors)

        except subprocess.CalledProcessError as e:
            errors.append(f"Compilation process failed: {e.stderr}")

    if errors:
        status = "Failure"
        print(
            f"\033[38;5;208m************** Compilation process failed with the following errors ************** \033[0m"
        )
        print(f"\033[38;5;208m****** {errors} ****** \033[0m")
    else:
        status = "Success"
        print(
            f"\033[38;5;208m************** Compilation process succeeded! **************\033[0m"
        )

    result = {
        "status": status,
        "errors": errors,
    }

    if abi:
        result["abi"] = abi

    return result
