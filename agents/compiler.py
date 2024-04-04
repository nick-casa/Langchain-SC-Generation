from typing import List, Dict, Union
import subprocess
import tempfile
import os
import json
import re

# install slither if needed:
# pip install slither-analyzer

def get_solidity_version(code: str) -> str:
    """
    Extracts the Solidity version from the pragma statement in the code.
    """
    match = re.search(r'pragma solidity\s+([^;]+);', code)
    return match.group(1).strip() if match else None

def run_static_analyses(contract_path: str) -> List[str]:
    """
    Runs Slither for static analysis on the Solidity contract.
    
    :param contract_path: Path to the Solidity contract file.
    :return: List of strings describing detected issues.
    """
    errors = []
    try:
        # Running Slither analysis and directing output to a temporary JSON file
        result = subprocess.run(['slither', contract_path, '--json', 'slither_output.json'],
                                capture_output=True, text=True, check=False)
        
        # Checking for Slither execution failure
        if result.returncode != 0:
            # Slither execution failed; we return the stderr output as an error message
            return [f"Slither failed to execute: {result.stderr}"]

        # Reading and parsing the Slither output JSON file
        with open('slither_output.json', 'r') as file:
            slither_output = json.load(file)
            
        # Extracting information about detected issues
        for detector in slither_output.get('detectors', []):
            # Constructing a meaningful message for each detected issue
            issue_description = f"{detector.get('check', 'Unknown Check')}: {detector.get('description', 'No description provided.')}"
            errors.append(issue_description)
            
    except Exception as e:
        errors.append(f"Error running static analysis: {str(e)}")
    
    finally:
        # Clean-up: remove the temporary Slither output file if it exists
        if os.path.exists('slither_output.json'):
            os.remove('slither_output.json')

    return errors

def run_static_analyses(contract_path: str, temp_dir: str) -> List[str]:
    """
    Placeholder for static analysis function. This should run tools like Slither
    and return a list of detected issues.
    """
    errors = []
    # Example static analysis call to Slither (assuming it's installed and configured)
    try:
        analysis_result = subprocess.run(['slither', contract_path, '--json', os.path.join(temp_dir, 'slither_output.json')],
                                         capture_output=True, text=True, check=False)
        if analysis_result.returncode == 0:
            with open(os.path.join(temp_dir, 'slither_output.json'), 'r') as slither_file:
                slither_output = json.load(slither_file)
                for issue in slither_output.get('detectors', []):
                    errors.append(f"{issue.get('check', 'Unknown')} - {issue.get('description', 'No description')}")
    except subprocess.CalledProcessError as e:
        errors.append("Slither static analysis failed to execute.")
    except json.JSONDecodeError:
        errors.append("Failed to parse Slither output.")

    return errors

def check_code(code: str, analysis_depth: str = "standard") -> Dict[str, Union[str, List[str]]]:
    errors: List[str] = []

    solidity_version = get_solidity_version(code)
    if solidity_version is None:
        return {"status": "Failure", "errors": ["No Solidity version specified in the pragma statement."]}

    if not set_solc_version(solidity_version):
        return {"status": "Failure", "errors": [f"Failed to set Solidity version to {solidity_version}. Ensure it is installed and try again."]}

    with tempfile.TemporaryDirectory() as temp_dir:
        contract_path = os.path.join(temp_dir, 'Contract.sol')
        with open(contract_path, 'w') as file:
            file.write(code)

        compile_cmd = ['solc', '--standard-json', '--allow-paths', temp_dir]
        compile_input = {
            'language': 'Solidity',
            'sources': {'Contract.sol': {'content': code}},
            'settings': {'outputSelection': {'*': {'*': ['abi', 'metadata', 'evm.bytecode', 'evm.bytecode.sourceMap']}}}
        }

        try:
            compile_result = subprocess.run(compile_cmd, input=json.dumps(compile_input), capture_output=True, text=True, check=False)
            compile_output = json.loads(compile_result.stdout)

            if 'errors' in compile_output:
                for error in compile_output['errors']:
                    if error.get('severity') in ['error', 'warning']:  # Customize based on severity needed
                        errors.append(error.get('formattedMessage', 'Unknown compilation issue.'))

            if not any('error' in e for e in errors):
                analysis_errors = run_static_analyses(contract_path)
                errors.extend(analysis_errors)

        except subprocess.CalledProcessError as e:
            errors.append(f"Compilation process failed: {e.stderr}")

    # Optionally reset solc to a default or previously used version after operation
    # set_solc_version("default")  # Be cautious about changing global settings

    return {"status": "Failure" if errors else "Success", "errors": errors}
