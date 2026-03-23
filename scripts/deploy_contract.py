import os
from solcx import compile_standard, install_solc
from web3 import Web3
import json

# Setup
RPC_URL = os.getenv("RPC_URL", "https://sepolia.base.org")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

def deploy():
    # Install solc
    install_solc("0.8.20")
    
    # Read contract
    with open("../contracts/ProofWork.sol", "r") as f:
        source = f.read()

    # Compile
    compiled = compile_standard({
        "language": "Solidity",
        "sources": {"ProofWork.sol": {"content": source}},
        "settings": {"outputSelection": {"*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}}}
    }, solc_version="0.8.20")

    bytecode = compiled["contracts"]["ProofWork.sol"]["ProofWork"]["evm"]["bytecode"]["object"]
    abi = compiled["contracts"]["ProofWork.sol"]["ProofWork"]["abi"]

    # Deploy
    account = w3.eth.account.from_key(PRIVATE_KEY)
    ProofWork = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # NOTE: You need to pass the generalistJudge address here
    generalistJudge = "0x..." 
    tx = ProofWork.constructor(generalistJudge).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 2000000,
        "gasPrice": w3.eth.gas_price
    })
    
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"Deployed to: {tx_receipt.contractAddress}")
    with open("../.env", "w") as f:
        f.write(f"CONTRACT_ADDRESS={tx_receipt.contractAddress}\n")

if __name__ == "__main__":
    deploy()
