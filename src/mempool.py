from src.validator import validate_transaction

class Mempool:
    def __init__(self, max_size=50):
        self.transactions = [] # List of full tx objects
        self.spent_utxos = set() # Set of (tx_id, index) to prevent double spends
        self.max_size = max_size

    def add_transaction(self, tx, utxo_manager):
        """Validate and add transaction."""
        if len(self.transactions) >= self.max_size:
            # Simple eviction policy: Reject if full (or implement fee-based eviction)
            return False, "Mempool is full"

        is_valid, msg, fee = validate_transaction(tx, utxo_manager, self)
        
        if is_valid:
            self.transactions.append({
                "tx": tx,
                "fee": fee,
                "timestamp": time.time() # For FIFO tie-breaking
            })
            # Mark inputs as spent in mempool to prevent Race Attacks
            for inp in tx["inputs"]:
                self.spent_utxos.add((inp["prev_tx"], inp["index"]))
            return True, f"Transaction added. Fee: {fee:.5f} BTC"
        else:
            return False, msg

    def remove_transaction(self, tx_id: str):
        """Remove transaction and its spent_utxo locks."""
        # Note: In mining, we remove the TX but we DON'T free the spent_utxos 
        # because they are now spent in the blockchain. 
        # This method is for dropping invalid/expired txs.
        tx_to_remove = next((t for t in self.transactions if t["tx"]["tx_id"] == tx_id), None)
        if tx_to_remove:
            self.transactions.remove(tx_to_remove)
            for inp in tx_to_remove["tx"]["inputs"]:
                if (inp["prev_tx"], inp["index"]) in self.spent_utxos:
                    self.spent_utxos.remove((inp["prev_tx"], inp["index"]))

    def get_top_transactions(self, n: int) -> list:
        """Return top N transactions by fee (highest first)."""
        # Sort by fee desc, then timestamp asc
        sorted_txs = sorted(self.transactions, key=lambda x: (-x["fee"], x["timestamp"]))
        return sorted_txs[:n]

    def clear(self):
        self.transactions = []
        self.spent_utxos = set()
        
import time # Needed for timestamp