import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

# Load artifact
with open('build/ProofWork.json', 'r') as f:
    artifact = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=artifact['abi'])

def post_test_bounty():
    description = "Write a Python script that calculates the Fibonacci sequence."
    judge_address = "0x0000000000000000000000000000000000000000" # Use generalist judge
    
    nonce = w3.eth.get_transaction_count(account.address)
    tx = contract.functions.postBounty(description, judge_address).build_transaction({
        'from': account.address,
        'value': w3.to_wei(0.001, 'ether'),
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price
    })
    
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Bounty Posted! Tx: {tx_hash.hex()}")

if __name__ == "__main__":
    post_test_bounty()