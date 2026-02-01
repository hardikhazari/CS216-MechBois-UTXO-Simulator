class UTXOManager:
    def __init__(self):
        # Dictionary mapping (tx_id, index) -> {amount, owner}
        self.utxo_set = {}

    def add_utxo(self, tx_id: str, index: int, amount: float, owner: str):
        """Add a new UTXO to the set."""
        self.utxo_set[(tx_id, index)] = {"amount": amount, "owner": owner}

    def remove_utxo(self, tx_id: str, index: int):
        """Remove a UTXO (when spent)."""
        if (tx_id, index) in self.utxo_set:
            del self.utxo_set[(tx_id, index)]

    def get_balance(self, owner: str) -> float:
        """Calculate total balance for an address."""
        balance = 0.0
        for utxo in self.utxo_set.values():
            if utxo["owner"] == owner:
                balance += utxo["amount"]
        return balance

    def exists(self, tx_id: str, index: int) -> bool:
        """Check if UTXO exists and is unspent."""
        return (tx_id, index) in self.utxo_set

    def get_utxos_for_owner(self, owner: str) -> list:
        """Get all UTXOs owned by an address (helper for creating txs)."""
        user_utxos = []
        for key, data in self.utxo_set.items():
            if data["owner"] == owner:
                user_utxos.append({
                    "tx_id": key[0],
                    "index": key[1],
                    "amount": data["amount"]
                })
        return user_utxos