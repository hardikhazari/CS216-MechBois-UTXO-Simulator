import sys
import os

# Add the project root directory to Python's search path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.utxo_manager import UTXOManager
from src.mempool import Mempool
from src.transaction import create_transaction
from src.mining import mine_block
# Now this import will work because Python can see the 'tests' folder
from tests.test_scenarios import run_tests as execute_tests
def initialize_genesis(utxo_mgr):
    """Setup initial state as per assignment reqs."""
    utxo_mgr.add_utxo("genesis", 0, 50.0, "Alice")
    utxo_mgr.add_utxo("genesis", 1, 30.0, "Bob")
    utxo_mgr.add_utxo("genesis", 2, 20.0, "Charlie")
    utxo_mgr.add_utxo("genesis", 3, 10.0, "David")
    utxo_mgr.add_utxo("genesis", 4, 5.0, "Eve")

def interactive_create_tx(utxo_mgr, mempool):
    print("\n--- Create New Transaction ---")
    sender = input("Enter sender: ").strip()
    
    # 1. Get Sender's UTXOs
    user_utxos = utxo_mgr.get_utxos_for_owner(sender)
    if not user_utxos:
        print("Error: Sender has no UTXOs/Funds.")
        return

    current_balance = sum(u["amount"] for u in user_utxos)
    print(f"Available Balance: {current_balance} BTC")
    
    recipient = input("Enter recipient: ").strip()
    try:
        amount = float(input("Enter amount to send: "))
        fee = float(input("Enter mining fee (optional, default 0): ") or 0)
    except ValueError:
        print("Invalid number.")
        return

    total_needed = amount + fee

    if current_balance < total_needed:
        print(f"Insufficient funds. Have {current_balance}, need {total_needed}.")
        return

    # 2. Select Inputs (Simple Coin Selection Algorithm: First-Fit)
    inputs = []
    input_sum = 0.0
    for u in user_utxos:
        inputs.append({
            "prev_tx": u["tx_id"],
            "index": u["index"],
            "owner": sender
        })
        input_sum += u["amount"]
        if input_sum >= total_needed:
            break
            
    # 3. Create Outputs
    outputs = [{"amount": amount, "address": recipient}]
    
    # Calculate Change
    change = input_sum - total_needed
    if change > 0:
        outputs.append({"amount": change, "address": sender})
        
    # 4. Create and Submit
    tx = create_transaction(inputs, outputs)
    success, msg = mempool.add_transaction(tx, utxo_mgr)
    
    if success:
        print(f"Transaction Created! ID: {tx['tx_id']}")
        print(msg)
    else:
        print(f"Transaction Failed: {msg}")

def main():
    utxo_manager = UTXOManager()
    mempool = Mempool()
    initialize_genesis(utxo_manager)

    while True:
        print("\n=== Bitcoin Transaction Simulator ===")
        print("Initial UTXOs (Genesis Block):")
        # Logic to display Genesis only if they exist? 
        # The prompt implies a static header, but dynamic is better.
        # We will just print the menu.
        
        print("Main Menu:")
        print("1. Create new transaction")
        print("2. View UTXO set")
        print("3. View mempool")
        print("4. Mine block")
        print("5. Run test scenarios")
        print("6. Exit")
        
        choice = input("Enter choice: ")

        if choice == '1':
            interactive_create_tx(utxo_manager, mempool)
        
        elif choice == '2':
            print("\n--- Current UTXO Set ---")
            for key, val in utxo_manager.utxo_set.items():
                print(f"Tx: {key[0]} [{key[1]}] -> {val['amount']} BTC ({val['owner']})")
        
        elif choice == '3':
            print(f"\n--- Mempool ({len(mempool.transactions)} txs) ---")
            for item in mempool.transactions:
                t = item["tx"]
                print(f"ID: {t['tx_id']} | Fee: {item['fee']} | Inputs: {len(t['inputs'])}")
        
        elif choice == '4':
            if not mempool.transactions:
                print("Mempool is empty. Create a transaction first.")
                continue

            miner = input("Enter miner name: ")
            
            # --- NEW: Transaction Selection ---
            print("\n--- Pending Transactions in Mempool ---")
            pending = mempool.transactions
            for i, item in enumerate(pending):
                t = item["tx"]
                # Try to get sender name for display
                sender = t["inputs"][0]["owner"] if t["inputs"] else "Unknown"
                print(f"[{i+1}] ID: {t['tx_id']} | Fee: {item['fee']:.5f} | Sender: {sender}")
            
            print("\nOptions:")
            print(" - Press ENTER to mine ALL (or top 5 highest fee)")
            print(" - Type numbers separated by comma (e.g. 1, 3) to mine specific ones")
            
            selection = input("Selection: ").strip()
            
            selected_txs = None
            if selection:
                try:
                    # Parse user input "1, 3" -> indices [0, 2]
                    indices = [int(x.strip()) - 1 for x in selection.split(",")]
                    selected_txs = []
                    for idx in indices:
                        if 0 <= idx < len(pending):
                            selected_txs.append(pending[idx])
                        else:
                            print(f"Warning: Transaction #{idx+1} does not exist. Skipping.")
                    
                    if not selected_txs:
                        print("No valid transactions selected. Aborting mining.")
                        continue
                except ValueError:
                    print("Invalid input. Please enter numbers like 1, 2.")
                    continue
            
            # Call mining with selection (if None, it defaults to auto-mining)
            mine_block(miner, mempool, utxo_manager, specific_txs=selected_txs)
            
        elif choice == '5':
            # Create a clean instance for tests to avoid messing up interactive state
            test_utxo = UTXOManager()
            initialize_genesis(test_utxo)
            test_mempool = Mempool()
            execute_tests(test_utxo, test_mempool, mine_block)
            
        elif choice == '6':
            print("Exiting.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()