# receive bitcoin_watcher

import mysql.connector
import time
import requests
from bit import Key

# Define the API endpoint and your API key if needed
API_URL = "https://blockchain.info/rawblock/"
BLOCKCHAIN_INFO_URL = "https://blockchain.info/rawblock/"

# Connect to MySQL database
def connect_to_db():
    try:
        db = mysql.connector.connect(
            host="192.168.0.107",
            user="root",
            passwd="admin",
            database="blockchain_db"
        )
        print("Connected to MySQL database")
        return db
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        exit()

db = connect_to_db()
cursor = db.cursor()

def latest_block_db():
    query = "SELECT MAX(block_number) FROM blockchain_db.receive_bitcoin_watcher"
    cursor.execute(query)
    result = cursor.fetchone()
    latest_block = result[0] if result[0] is not None else 0
    print(f"Latest block in database: {latest_block}")
    return latest_block

def monitor_blocks():
    latest_block = latest_block_db()
    print("Monitoring new blocks...")
    try:
        while True:
            print("Checking for new blocks...")
            current_block = requests.get("https://blockchain.info/q/getblockcount").text

            for block_number in range(latest_block + 1, int(current_block) + 1):
                try:
                    # Fetch the block with full transactions
                    response = requests.get(f"{BLOCKCHAIN_INFO_URL}{block_number}")
                    block = response.json()
                    print(f"Block fetched: {block_number}")

                    if 'tx' in block:
                        for tx in block['tx']:
                            print(f"Processing transaction {tx['hash']}")
                            store_transaction(tx, block_number)
                    
                    latest_block = block_number
                except requests.RequestException as e:
                    print(f"Error fetching block {block_number}: {e}")

            # Sleep for a bit before polling for new blocks again
            time.sleep(10)

    except Exception as e:
        print(f"Error while monitoring blocks: {e}")

def store_transaction(tx, block_number):
    global cursor, db
    try:
        if not db.is_connected():
            db = connect_to_db()
            cursor = db.cursor()

        # Initialize addresses as None
        from_address = None
        to_address = None

        # Debug print to check the structure of tx
        # print("Transaction Data:", tx)

        # Ensure the 'inputs' key exists and is not empty
        if 'inputs' in tx and len(tx['inputs']) > 0 and 'prev_out' in tx['inputs'][0] and 'addr' in tx['inputs'][0]['prev_out']:
            from_address = tx['inputs'][0]['prev_out']['addr']
        else:
            print("Warning: 'from_address' not found in transaction inputs")

        # Ensure the 'out' key exists and is not empty
        if 'out' in tx and len(tx['out']) > 0 and 'addr' in tx['out'][0]:
            to_address = tx['out'][0]['addr']
        else:
            print("Warning: 'to_address' not found in transaction outputs")

        transaction_hash = tx['hash']
        value = tx['out'][0]['value'] / 100000000  # Convert satoshis to BTC

        sql = """
        INSERT INTO blockchain_db.receive_bitcoin_watcher (from_address, to_address, transaction_hash, block_number, value)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE from_address=VALUES(from_address), to_address=VALUES(to_address), value=VALUES(value)
        """
        cursor.execute(sql, (from_address, to_address, transaction_hash, block_number, value))
        db.commit()
        print(f"Stored transaction {transaction_hash} with from_address {from_address} and to_address {to_address}")
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        db = connect_to_db()
        cursor = db.cursor()
    except Exception as e:
        print(f"Error storing transaction: {e}")

# Monitor new blocks and store transaction details
if __name__ == "__main__":
    monitor_blocks()
    db.close()
