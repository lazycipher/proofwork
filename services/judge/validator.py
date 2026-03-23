import os
import google.generativeai as genai
import logging

# Setup Logger
logger = logging.getLogger("ProofWorkValidator")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def evaluate_work(bounty_description, proof_data):
    """
    The Generalist Judge: Uses Gemini to evaluate work quality.
    """
    logger.info(f"AI Judge evaluating work for bounty: {bounty_description[:30]}...")

    prompt = f"""
    You are an expert ProofWork Judge. Review the work submitted by an AI agent for a bounty.
    
    Bounty Description: {bounty_description}
    Submitted Proof Content: {proof_data}
    
    Instructions:
    1. Score the work from 1-10 on accuracy, completion, and quality.
    2. If the score is >= 7, return "APPROVED" and a brief justification.
    3. If the score is < 7, return "REJECTED" and a clear reason for the failure.
    
    Format:
    RESULT: [APPROVED/REJECTED]
    REASON: [Your justification]
    """
    
    response = model.generate_content(prompt)
    
    logger.info(f"AI Judge decision: {response.text}")
    
    # Simple parser for the AI response
    return "APPROVED" in response.text
