from solana.rpc.api import Client
from solana.system_program import TransferParams, transfer
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.keypair import Keypair
import csv
import base64
import json

# Initialize Solana client
client = Client("https://api.mainnet-beta.solana.com")

# Load sender keypair from CSV file
csv_filename = 'solana_addresses.csv'

with open(csv_filename, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Assuming CSV columns are 'public_key' and 'private_key'
        public_key = row['Public Key']
        private_key = row['Private Key']
        sender_keypair = Keypair.from_secret_key(base64.b64decode(private_key))
        break  # Assuming only one keypair is in the CSV

# Define receiver public key (replace with actual receiver's public key)
receiver_pubkey = PublicKey("9bRDrYShoQ77MZKYTMoAsoCkU7dAR24mxYCBjXLpfEJx")

# Define transaction parameters
transfer_amount = 1000000  # Amount in lamports (1 SOL = 1,000,000,000 lamports)

# Create a transfer instruction
transfer_instruction = transfer(
    TransferParams(
        from_pubkey=sender_keypair.public_key,
        to_pubkey=receiver_pubkey,
        lamports=transfer_amount
    )
)

# Create a transaction and add the transfer instruction
transaction = Transaction().add(transfer_instruction)

# Prepare data for storage
transaction_data = {
    "recent_blockhash": str(transaction.recent_blockhash),
    "fee_payer": str(transaction.fee_payer),
    "instructions": [
        {
            "program_id": str(instr.program_id),
            "keys": [{"pubkey": str(key.pubkey), "is_signer": key.is_signer, "is_writable": key.is_writable} for key in instr.keys],
            "data": instr.data.hex()
        }
        for instr in transaction.instructions
    ]
}

# Store raw transaction data in JSON format
csv_filename = "unsigned_transactions.json"

with open(csv_filename, mode='w', newline='') as file:
    json.dump(transaction_data, file, indent=4)

print(f"Unsigned transaction data has been written to {csv_filename}")
