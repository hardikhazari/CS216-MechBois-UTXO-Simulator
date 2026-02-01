from src.transaction import generate_tx_id

def mine_block(miner_address: str, mempool, utxo_manager, specific_txs=None):
    """
    Mines a block.
    If 'specific_txs' is provided, it mines ONLY those.
    Otherwise, it mines the top 5 highest-fee transactions.
    """
    if not mempool.transactions:
        print("Mempool is empty. Nothing to mine.")
        return

    # 1. Select transactions
    if specific_txs is not None:
        candidates = specific_txs
        print(f"Mining block with {len(candidates)} USER-SELECTED transactions...")
    else:
        # Default behavior: Mine top 5 by fee
        candidates = mempool.get_top_transactions(5)
        print(f"Mining block with top {len(candidates)} transactions...")

    total_fee = 0.0
    tx_ids_to_remove = []

    # 2. Process transactions
    for item in candidates:
        tx = item["tx"]
        total_fee += item["fee"]
        tx_ids_to_remove.append(tx["tx_id"])

        # Remove Inputs (Destroy UTXOs)
        for inp in tx["inputs"]:
            utxo_manager.remove_utxo(inp["prev_tx"], inp["index"])

        # Add Outputs (Create UTXOs)
        for i, out in enumerate(tx["outputs"]):
            utxo_manager.add_utxo(tx["tx_id"], i, out["amount"], out["address"])

    # 3. Coinbase Transaction (Miner Reward)
    coinbase_tx_id = generate_tx_id()
    utxo_manager.add_utxo(coinbase_tx_id, 0, total_fee, miner_address)
    
    # 4. Clean up Mempool
    # Remove mined transactions from main list
    mempool.transactions = [t for t in mempool.transactions if t["tx"]["tx_id"] not in tx_ids_to_remove]
    
    # Remove spent_utxos locks
    for item in candidates:
        for inp in item["tx"]["inputs"]:
            key = (inp["prev_tx"], inp["index"])
            if key in mempool.spent_utxos:
                mempool.spent_utxos.remove(key)

    print(f"Block mined! Miner {miner_address} earned {total_fee:.5f} BTC.")
    print(f"Transactions confirmed: {tx_ids_to_remove}")