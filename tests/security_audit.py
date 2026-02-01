import sys
import os
import time

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.utxo_manager import UTXOManager
from src.mempool import Mempool
from src.transaction import create_transaction
from src.mining import mine_block

def print_result(test_name, success, message=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {test_name}")
    if not success:
        print(f"   Reason: {message}")

def run_security_audit():
    print("\n" + "="*40)
    print("🔒 STARTING SECURITY & INTEGRITY AUDIT")
    print("="*40 + "\n")

    # --- SETUP ---
    utxo = UTXOManager()
    mempool = Mempool()
    
    # Genesis: Alice=50, Bob=30
    utxo.add_utxo("genesis", 0, 50.0, "Alice")
    utxo.add_utxo("genesis", 1, 30.0, "Bob")

    # --- TEST 1: The "Negative Money" Printer ---
    # Attempt: Create a transaction with negative output (printing money)
    inputs = [{"prev_tx": "genesis", "index": 0, "owner": "Alice"}]
    outputs = [
        {"amount": -100.0, "address": "Bob"}, # Malicious negative amount
        {"amount": 150.0, "address": "Alice"} # Trying to gain free money
    ]
    tx_neg = create_transaction(inputs, outputs)
    success, msg = mempool.add_transaction(tx_neg, utxo)
    print_result("Detect Negative Outputs", not success, msg)

    # --- TEST 2: The "Inflation" Attack ---
    # Attempt: Output total (100) > Input total (50)
    outputs_inf = [{"amount": 100.0, "address": "Bob"}]
    tx_inf = create_transaction(inputs, outputs_inf)
    success, msg = mempool.add_transaction(tx_inf, utxo)
    print_result("Detect Inflation (In < Out)", not success, msg)

    # --- TEST 3: The "Signature Spoofing" Attack ---
    # Attempt: Eve tries to spend Alice's coin
    inputs_theft = [{"prev_tx": "genesis", "index": 0, "owner": "Eve"}] # Eve claims Alice's UTXO
    outputs_theft = [{"amount": 50.0, "address": "Eve"}]
    tx_theft = create_transaction(inputs_theft, outputs_theft)
    success, msg = mempool.add_transaction(tx_theft, utxo)
    print_result("Detect Signature Spoofing", not success, msg)

    # --- TEST 4: The "Double Spend" (Mempool Conflict) ---
    # 1. Valid TX: Alice -> Bob (50)
    outputs_valid = [{"amount": 50.0, "address": "Bob"}]
    tx_valid = create_transaction(inputs, outputs_valid)
    mempool.add_transaction(tx_valid, utxo)
    
    # 2. Malicious TX: Alice -> Eve (50) using SAME input
    tx_double = create_transaction(inputs, [{"amount": 50.0, "address": "Eve"}])
    success, msg = mempool.add_transaction(tx_double, utxo)
    print_result("Prevent Mempool Double Spend", not success, msg)

    # --- TEST 5: The "Replay" Attack (Spending Spent Coins) ---
    # Mine the first block to confirm Alice's spend
    mine_block("Miner1", mempool, utxo)
    
    # Attempt: Alice tries to spend the 'genesis:0' coin AGAIN after it was mined
    success, msg = mempool.add_transaction(tx_valid, utxo) # Replaying old TX
    print_result("Prevent Replay Attack (Spent UTXO)", not success, msg)

    # --- TEST 6: The "Non-Existent Input" Attack ---
    # Attempt: Spending a coin that never existed
    inputs_fake = [{"prev_tx": "fake_tx_id", "index": 0, "owner": "Alice"}]
    tx_fake = create_transaction(inputs_fake, [{"amount": 10.0, "address": "Bob"}])
    success, msg = mempool.add_transaction(tx_fake, utxo)
    print_result("Detect Non-Existent Input", not success, msg)

    print("\n" + "="*40)
    print("AUDIT COMPLETE")
    print("="*40)

if __name__ == "__main__":
    run_security_audit()