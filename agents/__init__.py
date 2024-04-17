# agent/__init__.py
from .query import process_query
from .llm import SmartContractGenerator

# from .merger import select_optimal_code
from .compiler import check_code, get_solidity_version, set_solc_version

# from .deployer import deploy_code, test_deployed_contract
from .deployer_v1 import deploy_contract

__all__ = [
    "process_query",
    "SmartContractGenerator",
    "get_solidity_version",
    "set_solc_version",
    # "select_optimal_code",
    "check_code",
    "deploy_contract",
]
