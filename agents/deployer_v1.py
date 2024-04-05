from typing import Dict, List
import json
from web3 import Web3, HTTPProvider
from solcx import compile_standard, install_solc
import compiler as c
# deployer.py
import os
import requests

def deploy_contract(code: str) -> Dict[str, str]:
    errors: List[str] = []

    version = c.get_solidity_version(contract_source)
    print('Solidity version:', version)
    c.set_solc_version(version)

    # Compile the Solidity contract
    compiled_sol = compile_standard({
        "language": "Solidity",
        "sources": {
            "Contract.sol": {
                "content": contract_source
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    }, solc_version=version[1:])

    # Get the contract interface
    contract_id, contract_interface = compiled_sol['contracts']['Contract.sol'].popitem()

    # Get the bytecode and ABI
    bytecode = contract_interface['evm']['bytecode']['object']
    abi = contract_interface['abi']

    print('bytecode:', bytecode)
    print('abi:', abi)

    try:
        # Connect to Ganache
        w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

        # Create a contract instance
        contract = w3.eth.contract(abi=abi, bytecode=bytecode)

        # Get the account to deploy from -> Ganache generates testing accounts and we use the first one of those
        account = w3.eth.accounts[0]

        # Check if the contract has a constructor
        constructor_abi = next((abi for abi in contract_interface['abi'] if abi['type'] == 'constructor'), None)

        if constructor_abi:
            # If the contract has a constructor, get the constructor parameters from the user
            constructor_args = []
            for input_param in constructor_abi['inputs']:
                param_type = input_param['type']
                param_name = input_param['name']
                # param_value = input(f"Enter the value for {param_name} ({param_type}): ")
                # could replace the hardcoded values below with prompts for param_values from the user, but as we are just
                if param_type.startswith('uint') or param_type.startswith('int'):
                    param_value = int(5)
                elif param_type == 'bool':
                    param_value = bool(True) # an arbitrary bool
                elif param_type == 'address':
                    param_value = account # a sample address that we know exist
                else:
                    param_value = None
                    errors.append(f"Contract's constructor required the type {param_type}, which is unsupported by our application's deployment testing.")
                # Note that more conversions may be needed to automatically test
                constructor_args.append(param_value)

            # Deploy the contract with constructor arguments
            tx_hash = contract.constructor(*constructor_args).transact({'from': account})
        else:
            # If the contract doesn't have a constructor, deploy without arguments
            tx_hash = contract.constructor().transact({'from': account})

        # Wait for the transaction to be mined and get the transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        # Get the contract address
        contract_address = tx_receipt.contractAddress

        print(f"Contract deployed at address: {contract_address}")

        # Return the deployed contract instance
        deployed_contract = w3.eth.contract(address=contract_address, abi=abi)
    except requests.exceptions.ConnectionError as e:
        errors.append("Connection error. Make sure Ganache is running on port 8545. You can start Ganache using this command in terminal: ganache-cli")
    except Exception as e:
        print(type(e))
        errors.append(str(e))

    result = {
        "status": "Failure" if errors else "Success",
        "errors": errors,
    }

    return result


if __name__ == "__main__":
    # import environment variables
    # from dotenv import load_dotenv
    # import os
    #
    # # Load environment variables from parent folder
    # dot_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
    # load_dotenv(dot_env_path)
    # wallet_address = os.getenv("WALLET_ADDRESS")
    # os.environ["WALLET_ADDRESS"] = wallet_address
    # private_key = os.getenv("PRIVATE_KEY")
    # os.environ["PRIVATE_KEY"] = private_key
    #
    # print(wallet_address, '\n', private_key)

    # sample solidity contract source code
    contract_source = '''
    pragma solidity ^0.8.0;

    contract MyContract {
        uint256 public myVariable;

        constructor(uint256 _initialValue) {
            myVariable = _initialValue;
        }

        function setVariable(uint256 _newValue) public {
            myVariable = _newValue;
        }
    }
    '''
    result = deploy_contract(contract_source)
    print(result)