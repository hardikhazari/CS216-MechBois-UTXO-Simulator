import time
import random

def generate_tx_id():
    """Generates a unique transaction ID."""
    return f"tx_{int(time.time())}_{random.randint(1000, 9999)}"

def create_transaction(inputs, outputs):
    """
    Creates a transaction dictionary.
    inputs: list of {"prev_tx": str, "index": int, "owner": str}
    outputs: list of {"amount": float, "address": str}
    """
    return {
        "tx_id": generate_tx_id(),
        "inputs": inputs,
        "outputs": outputs
    }