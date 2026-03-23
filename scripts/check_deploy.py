from web3 import Web3
import json
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Configuration
RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
account_address = "0xBD9f06cb7Bc56660D8b3BCc31Ba65CF0B5496857" # Your Wallet

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

# Simple compiled contract (ABI & Bytecode)
# In a real environment, you'd use solc or hardhat to compile.
# For now, let's write a simple deployer.
# Assuming contracts/ProofWork.sol exists.
# We'll use a small script to verify the connection first.

def check_connection():
    if w3.is_connected():
        print(f"Connected to {RPC_URL}")
        print(f"Balance of {account.address}: {w3.from_wei(w3.eth.get_balance(account.address), 'ether')} ETH")
        return True
    return False

if __name__ == "__main__":
    if check_connection():
        print("Ready to deploy. Please run a compiler script or use Remix to deploy and copy the address here.")
