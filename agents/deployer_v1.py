from typing import Dict, Union
import json
from web3 import Web3

# deployer.py
import os


# Note, this doesn't work yet
def deploy_code(code: str, w3: Web3, account: str, gas_price: int, gas_limit: int) -> Dict[str, str]:
    """
    Deploys the compiled code to a target environment and returns the deployment status.

    :param code: The code to be deployed.
    :param w3: The Web3 instance to interact with the Ethereum network.
    :param account: The Ethereum account to deploy from.
    :param gas_price: The price of gas in wei.
    :param gas_limit: The maximum amount of gas to use for the deployment.
    :return: A dictionary containing the status of the deployment.
    """

    w3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/6c263f7d8cce432fbd45987fe53c2b72'))

    print(w3.eth.get_block_number())

    wallet_address = os.environ["WALLET_ADDRESS"]
    private_key = os.environ["PRIVATE_KEY"]

    print(w3.__dict__)
    # Compile the Solidity code
    compiled_sol = compile_solidity(code)

    # Get the bytecode and ABI from the compiled Solidity code
    bytecode = compiled_sol['contracts'][compiled_sol['contracts'].keys()[0]]['bin']
    abi = json.loads(compiled_sol['contracts'][compiled_sol['contracts'].keys()[0]]['abi'])

    # Deploy the contract
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    transaction = contract.constructor().buildTransaction({
        'from': account,
        'gasPrice': gas_price,
        'gas': gas_limit
    })

    # Sign the transaction with the private key of the account
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)

    # Send the transaction to the network
    receipt = w3.eth.send_transaction(signed_transaction)

    # Return the deployment status
    return {
        'contract_address': receipt['contractAddress'],
        'status': receipt['status']
    }

# Helper functions
def compile_solidity(code: str) -> Dict:
    # Compile the Solidity code using the Solidity compiler
    # (not shown here as it depends on the specific Solidity compiler setup)
    pass
    # return compiled_sol


if __name__ == "__main__":
    # import environment variables
    from dotenv import load_dotenv
    import os

    # Load environment variables from parent folder
    dot_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
    load_dotenv(dot_env_path)
    wallet_address = os.getenv("WALLET_ADDRESS")
    os.environ["WALLET_ADDRESS"] = wallet_address
    private_key = os.getenv("PRIVATE_KEY")
    os.environ["PRIVATE_KEY"] = private_key

    print(wallet_address, '\n', private_key)