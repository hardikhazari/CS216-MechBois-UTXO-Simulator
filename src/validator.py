def validate_transaction(tx, utxo_manager, mempool):
    """
    Validates a transaction against UTXO set and Mempool.
    Returns: (is_valid: bool, message: str, fee: float)
    """
    input_sum = 0.0
    output_sum = 0.0
    
    # 1. Check if inputs exist and calculate input sum
    used_inputs_in_this_tx = set()
    
    for inp in tx["inputs"]:
        tx_key = (inp["prev_tx"], inp["index"])
        
        # Rule 1: Input must exist in UTXO set
        if not utxo_manager.exists(inp["prev_tx"], inp["index"]):
            return False, f"Input {tx_key} does not exist in UTXO set", 0.0
        
        # Rule 2: No double spending within the same transaction
        if tx_key in used_inputs_in_this_tx:
            return False, f"Double spend detected within transaction inputs", 0.0
        used_inputs_in_this_tx.add(tx_key)

        # Rule 5: No conflict with mempool (Race Attack Check)
        if tx_key in mempool.spent_utxos:
            return False, f"UTXO {tx_key} already spent in pending transaction (Mempool conflict)", 0.0

        # Verify owner (Simple signature simulation)
        utxo_data = utxo_manager.utxo_set[tx_key]
        if utxo_data["owner"] != inp["owner"]:
             return False, f"Signature mismatch: {inp['owner']} cannot spend {utxo_data['owner']}'s UTXO", 0.0

        input_sum += utxo_data["amount"]

    # Calculate output sum
    for out in tx["outputs"]:
        # Rule 4: No negative amounts
        if out["amount"] < 0:
            return False, "Output amount cannot be negative", 0.0
        output_sum += out["amount"]

    # Rule 3: Sum(inputs) >= Sum(outputs)
    if input_sum < output_sum:
        return False, f"Insufficient funds: Inputs ({input_sum}) < Outputs ({output_sum})", 0.0

    fee = input_sum - output_sum
    return True, "Transaction Valid", fee