from src.transaction import create_transaction

def run_tests(utxo_manager, mempool, mine_block_func):
    print("\n--- Running Test Scenarios ---")
    
    # Helper to reset state for tests (Optional, but clean)
    mempool.clear()
    
    # Test 1: Basic Valid Transaction
    print("\n[Test 1] Basic Valid Transaction (Alice -> Bob)")
    # Alice has 50 BTC at (genesis, 0)
    inputs = [{"prev_tx": "genesis", "index": 0, "owner": "Alice"}]
    # Send 10 to Bob, 39.999 Change to Alice (0.001 Fee)
    outputs = [
        {"amount": 10.0, "address": "Bob"},
        {"amount": 39.999, "address": "Alice"}
    ]
    tx1 = create_transaction(inputs, outputs)
    success, msg = mempool.add_transaction(tx1, utxo_manager)
    print(f"Result: {success} - {msg}")

    # Test 3 & 4: Double Spend / Mempool Conflict
    print("\n[Test 3/4] Double Spend Attempt")
    # Try to spend the SAME input (genesis, 0) again
    # Sending to Charlie
    inputs_bad = [{"prev_tx": "genesis", "index": 0, "owner": "Alice"}]
    outputs_bad = [{"amount": 50.0, "address": "Charlie"}]
    tx_bad = create_transaction(inputs_bad, outputs_bad)
    
    success, msg = mempool.add_transaction(tx_bad, utxo_manager)
    print(f"Result (Should Fail): {success} - {msg}")

    # Test 5: Insufficient Funds
    print("\n[Test 5] Insufficient Funds")
    # Bob has 30 BTC (genesis, 1). Try to send 35.
    inputs_broke = [{"prev_tx": "genesis", "index": 1, "owner": "Bob"}]
    outputs_broke = [{"amount": 35.0, "address": "Charlie"}]
    tx_broke = create_transaction(inputs_broke, outputs_broke)
    success, msg = mempool.add_transaction(tx_broke, utxo_manager)
    print(f"Result: {success} - {msg}")

    # Test 6: Negative Amount
    print("\n[Test 6] Negative Output")
    outputs_neg = [{"amount": -5.0, "address": "Bob"}]
    tx_neg = create_transaction(inputs, outputs_neg) # Reuse valid inputs
    success, msg = mempool.add_transaction(tx_neg, utxo_manager)
    print(f"Result: {success} - {msg}")

    # Test 8: Race Attack (First Seen Rule)
    print("\n[Test 8] Race Attack Simulation")
    mempool.clear() # Clear mempool to reset locks
    # 1. Low fee tx arrives
    out_low = [{"amount": 10.0, "address": "Bob"}, {"amount": 39.999, "address": "Alice"}] # Fee 0.001
    tx_low = create_transaction(inputs, out_low)
    mempool.add_transaction(tx_low, utxo_manager)
    print("1. Low fee transaction broadcast first.")
    
    # 2. High fee tx arrives trying to spend same input
    out_high = [{"amount": 10.0, "address": "Bob"}, {"amount": 39.0, "address": "Alice"}] # Fee 1.0
    tx_high = create_transaction(inputs, out_high)
    success, msg = mempool.add_transaction(tx_high, utxo_manager)
    print(f"2. High fee transaction broadcast second.")
    print(f"Result (First-Seen Rule): {success} - {msg}")

    # Clean up for main execution
    mempool.clear()
    print("\n--- Tests Completed ---")