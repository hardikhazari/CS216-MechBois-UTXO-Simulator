# CS216 – MechBois UTXO Simulator

## Team Information

**Team Name:** MechBois

**Team Members:**
- Harsh Bhalla – 240003033
- Hardik Sanjeev Hazari – 240003032
- Jatin Singh – 240003035
- Abhinav Jain – 240003003

## Project Overview

This project is a simplified UTXO-based blockchain simulator developed as part of **CS216: Introduction to Blockchain**.  
It models the core ideas of Bitcoin’s transaction system, including UTXO management, transaction validation, mempool handling, mining, and security checks, in a single-node, educational setting.

The simulator is menu-driven and allows users to create transactions, view UTXOs, manage a mempool, mine blocks, and run predefined test scenarios.

## Repository Structure

### Root Directory
- README.md – Project documentation
- sample_output.txt – Sample execution output

## Getting the Repository

Clone the repository and navigate to the project directory:


git clone https://github.com/hardikhazari/CS216-MechBois-UTXO-Simulator.git <br>
cd CS216-MechBois-UTXO-Simulator

<br>
# How to Run the Program
  >Ensure you are in the project root directory.
  >Run the main program using:
    python3 src/main.py <br>
  >A menu-driven interface will appear, allowing you to:<br>
    >>Create new transactions <br>
    >>View the current UTXO set <br>
    >>View mempool transactions <br>
    >>Mine blocks  <br>
    >>Run test scenarios <br>

### Source Code (src/)
- main.py – Main program entry point
- utxo_manager.py – UTXO set management
- transaction.py – Transaction structure and ID generation
- validator.py – Transaction validation rules
- mempool.py – Mempool handling and conflict prevention
- mining.py – Block mining and UTXO updates
- __init__.py

### Tests (tests/)
- test_scenarios.py – Functional test cases
- security_audit.py – Security and adversarial tests
- __init__.py

## How to Run the Program

1. Ensure you are in the project root directory.
2. Run the main program using:

3. A menu-driven interface will appear, allowing you to:
- Create new transactions
- View the current UTXO set
- View mempool transactions
- Mine blocks
- Run test scenarios

## Design Explanation

### 1. UTXO Manager
- Maintains the global UTXO set as a mapping from `(tx_id, output_index)` to `{amount, owner}`.
- Acts as the single source of truth for balances and unspent outputs.
- Supports adding, removing, querying, and listing UTXOs for transaction creation.

### 2. Transactions
Transactions consist of:
- Inputs: references to previous UTXOs
- Outputs: newly created UTXOs
- Each transaction is assigned a pseudo-unique transaction ID using timestamp and randomness.
- The system follows the UTXO model, similar to Bitcoin.

### 3. Validator
- Centralized module enforcing transaction correctness.
- Validation rules include:
  - Input UTXOs must exist and be unspent
  - No double spending within a transaction
  - No conflicts with mempool (race attack prevention)
  - Ownership verification (logical signature check)
  - No negative output values
  - Sum(inputs) ≥ Sum(outputs)
  - Transaction fee is computed implicitly as the difference

### 4. Mempool
- Temporarily stores unconfirmed transactions.
- Uses a `spent_utxos` lock mechanism to prevent:
  - Double spending
  - Race-condition attacks
- Supports fee-based prioritization and FIFO tie-breaking.

### 5. Mining
- Simulates block creation in a single-node environment.
- Two mining modes:
  - User-selected transactions
  - Automatic selection of top 5 transactions by fee
- Mining process:
  - Consumes input UTXOs
  - Creates new output UTXOs
  - Rewards miner using a coinbase-style transaction (fees only)
  - Mined transactions are removed from the mempool and locks are cleared

## Testing

### Functional Tests (test_scenarios.py)
- Valid transaction execution
- Double-spend attempts
- Insufficient funds
- Negative output rejection
- Race-condition / first-seen rule simulation

### Security Audit (security_audit.py)
- Simulates common blockchain attacks to verify robustness:
  - Money printing via negative outputs
  - Signature spoofing (ownership theft)
  - Mempool double-spend attacks
  - Replay attacks using spent UTXOs
  - Non-existent input attacks
- All attacks are correctly detected and rejected by the system.

## Dependencies
- Python 3.13.1
- Only standard Python libraries are used  
(No external packages required)

## Assumptions and Limitations
- Single-node simulation (no networking or consensus)
- No cryptographic signatures or proof-of-work
- No forks or longest-chain rule
- Miner reward consists only of transaction fees
- Designed for educational purposes, not production use

## Conclusion

This simulator demonstrates the core mechanics and security principles of a UTXO-based blockchain system with clean modular design, validation logic, and adversarial testing.  
It provides a clear and practical understanding of how Bitcoin-like systems manage transactions and prevent common attacks.
