import os
import time
import logging
import json
from web3 import Web3
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BountyAgent")

# Configuration
RPC_URL = os.getenv("RPC_URL", "https://ethereum-sepolia-rpc.publicnode.com")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)
client = genai.Client(api_key=GEMINI_API_KEY)

# Contract Setup
with open('build/ProofWork.json', 'r') as f:
    artifact = json.load(f)
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=artifact['abi'])

def perform_work(description):
    """
    Generate work (e.g., Python code) using Gemini.
    """
    logger.info(f"Generating work for: {description}")
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=f"Provide a concise Python solution for: {description}",
    )
    return response.text

def evaluate_and_claim(bounty_id):
    bounty = contract.functions.bounties(bounty_id).call()
    description = bounty[2] 
    logger.info(f"Analyzing Bounty {bounty_id}: {description}")
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=f"Can you complete a task described as '{description}'? Answer strictly with YES or NO.",
    )
    return "YES" in response.text.strip().upper()

def run():
    logger.info("Bounty Agent monitoring...")
    last_block = w3.eth.block_number
    
    while True:
        try:
            current_block = w3.eth.block_number
            if current_block > last_block:
                events = contract.events.BountyPosted.get_logs(from_block=last_block + 1, to_block=current_block)
                for event in events:
                    bounty_id = event['args']['id']
                    if evaluate_and_claim(bounty_id):
                        logger.info(f"Claiming Bounty {bounty_id}")
                        
                        # 1. Claim
                        nonce = w3.eth.get_transaction_count(account.address)
                        tx = contract.functions.claimBounty(bounty_id).build_transaction({
                            'from': account.address, 'nonce': nonce, 'gas': 200000, 'gasPrice': w3.eth.gas_price
                        })
                        tx_hash = w3.eth.send_raw_transaction(w3.eth.account.sign_transaction(tx, PRIVATE_KEY).raw_transaction)
                        w3.eth.wait_for_transaction_receipt(tx_hash)
                        logger.info(f"Claimed Bounty {bounty_id}")

                        # 2. Do the Work
                        bounty = contract.functions.bounties(bounty_id).call()
                        solution = perform_work(bounty[2])
                        proof_hash = w3.keccak(text=solution)

                        # 3. Submit Proof
                        nonce = w3.eth.get_transaction_count(account.address)
                        tx = contract.functions.submitProof(bounty_id, proof_hash).build_transaction({
                            'from': account.address, 'nonce': nonce, 'gas': 300000, 'gasPrice': w3.eth.gas_price
                        })
                        tx_hash = w3.eth.send_raw_transaction(w3.eth.account.sign_transaction(tx, PRIVATE_KEY).raw_transaction)
                        logger.info(f"Proof submitted for {bounty_id}: {tx_hash.hex()}")
                
                last_block = current_block
            time.sleep(15)
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    run()
