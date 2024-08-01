import csv
import requests
import mysql.connector
from mysql.connector import Error

# Connect to MySQL database
try:
    db = mysql.connector.connect(
        host="192.168.1.10",
        user="root",
        passwd="admin",
        database="blockchain_db"
    )
    cursor = db.cursor()
except Error as e:
    print(f"Error connecting to MySQL: {e}")
    exit()

# Function to fetch and store transaction details
def store_transaction_details(to_address):
    print(f"Processing address: {to_address}")

    # Get the latest block number
    try:
        response = requests.get("https://blockchain.info/q/getblockcount")
        response.raise_for_status()  # Check if request was successful
        latest_block = int(response.text)
    except requests.RequestException as e:
        print(f"Error fetching latest block number: {e}")
        return

    # Check the latest N blocks for transactions (N can be adjusted as needed)
    for block_num in range(latest_block, latest_block - 300, -1):
        try:
            # Fetch block details from Blockchain.info API
            response = requests.get(f"https://blockchain.info/rawblock/{block_num}")
            response.raise_for_status()  # Check if request was successful
            block_data = response.json()
        except requests.RequestException as e:
            print(f"Error fetching block {block_num}: {e}")
            continue
        
        # Process transactions in the block
        for tx in block_data.get('tx', []):
            for out in tx.get('out', []):
                if 'addr' in out and out['addr'].lower() == to_address.lower():
                    from_address = tx['inputs'][0]['prev_out']['addr'] if tx['inputs'] else None
                    transaction_hash = tx['hash']
                    value = out['value'] / 1e8  # Convert satoshis to BTC
                    gas_price = None
                    block_number = tx['block_height']

                    try:
                        # Check if the transaction hash already exists in the database
                        cursor.execute("""
                            SELECT COUNT(*) FROM blockchain_db.receive_blockchain_watcher WHERE transaction_hash = %s
                        """, (transaction_hash,))
                        if cursor.fetchone()[0] == 0:
                            print(f"Storing transaction to_address: {to_address}, from_address: {from_address}, transaction_hash: {transaction_hash}, value: {value}, gas_price: {gas_price}, block_number: {block_number}")

                            # Insert transaction details into MySQL
                            cursor.execute("""
                                INSERT INTO blockchain_db.receive_blockchain_watcher (to_address, from_address, transaction_hash, value, gas_price, block_number)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (to_address, from_address, transaction_hash, value, gas_price, block_number))
                            db.commit()
                            print("Transaction stored successfully")
                        else:
                            print(f"Transaction {transaction_hash} already exists in the database")
                    except Error as e:
                        print(f"Error inserting transaction into database: {e}")

# Read the Bitcoin addresses from CSV and process each one
with open('/home/ubuntu/Wallet_watcher/Ethereum_blockchain/Address_generation/ethereum_address.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header
    for row in reader:
        to_address = row[3]
        store_transaction_details(to_address)

# Close the MySQL connection
cursor.close()
db.close()
