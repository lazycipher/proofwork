from web3 import Web3
import json
import os
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

# Load compiled contract
with open('build/ProofWork.json', 'r') as f:
    artifact = json.load(f)

abi = artifact['abi']
bytecode = artifact['bytecode']

# Instantiate contract
ProofWork = w3.eth.contract(abi=abi, bytecode=bytecode)

# Build constructor transaction
print(f"Deploying from: {account.address}")
# The constructor takes _generalistJudge address
# For now, let's use a dummy address for the generalist judge
generalist_judge = account.address 

tx = ProofWork.constructor(generalist_judge).build_transaction({
    'from': account.address,
    'nonce': w3.eth.get_transaction_count(account.address),
    'gas': 2000000,
    'gasPrice': w3.eth.gas_price
})

# Sign transaction
signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

# Send transaction
print("Sending transaction...")
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f"Deployed to: {tx_receipt.contractAddress}")
with open('CONTRACT_ADDRESS.txt', 'w') as f:
    f.write(tx_receipt.contractAddress)
