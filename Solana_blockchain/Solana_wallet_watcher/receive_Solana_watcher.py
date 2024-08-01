import mysql.connector
import time
import requests
import json

# Define the API endpoint
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

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

def get_latest_block_from_db():
    query = "SELECT MAX(slot) FROM blockchain_db.receive_solana_watcher"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0] if result[0] is not None else 0

def fetch_current_slot():
    try:
        response = requests.post(SOLANA_RPC_URL, json={"jsonrpc":"2.0","id":1,"method":"getSlot"})
        response.raise_for_status()  # Check if request was successful
        data = response.json()
        if "result" in data:
            return data["result"]
        else:
            print(f"Unexpected response structure: {data}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching current slot: {e}")
        return None
# if transcation is my  then stored  saves in my tx all tx is not saved 
def fetch_block_transactions(slot):
    try:
        response = requests.post(SOLANA_RPC_URL, json={
            "jsonrpc":"2.0","id":1,"method":"getBlock",
            "params":[slot, {"transactionDetails":"full"}]#if to address is fetch from data table than store in database
        })
        response.raise_for_status()  # Check if request was successful
        data = response.json()
        if "result" in data:
            return data["result"]
        else:
            print(f"Unexpected response structure: {data}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching block transactions for slot {slot}: {e}")
        return None

def store_transaction(tx, slot, block_number):
    try:
        transaction_data = tx.get('transaction', {})

        message = transaction_data.get('message', {})
        account_keys = message.get('accountKeys', [])

        from_address = account_keys[0]
        to_address = account_keys[1]
        transaction_hash = transaction_data.get('signatures', [None])[0]

        instruction_data = None
        fee = 0
        
        instructions = message.get('instructions', [])
        for instr in instructions:
            if 'parsed' in instr:
                instruction_data = json.dumps(instr)
                break

        meta = tx.get('meta', {})
        if meta is None:
            meta = {}
        fee = meta.get('fee', 0)
        
        if instruction_data is None:
            instruction_data = json.dumps(instructions)
        
        sql = """
        INSERT INTO blockchain_db.receive_solana_watcher (transaction_hash, slot, from_address, to_address, instruction_data, fee, block_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE from_address=VALUES(from_address), to_address=VALUES(to_address), instruction_data=VALUES(instruction_data), fee=VALUES(fee), block_number=VALUES(block_number)
        """

        cursor.execute(sql, (transaction_hash, slot, from_address, to_address, instruction_data, fee, block_number))
        db.commit()
        print(f"Stored transaction {transaction_hash}")
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    except KeyError as e:
        print(f"KeyError: {e} in transaction {tx}")
    except Exception as e:
        print(f"Error storing transaction: {e}")

def monitor_blocks():
    latest_block = get_latest_block_from_db()
    print("Monitoring new blocks...")
    try:
        while True:
            current_slot = fetch_current_slot()
            if current_slot is None:
                time.sleep(2)
                continue

            for slot in range(latest_block + 1, int(current_slot) + 1):

                    try:
                        block = fetch_block_transactions(slot)
                        if block:
                            block_number = block.get('blockHeight', slot)
                            if block_number is None:
                                print(f"Block number is : {slot}")
                                block_number = slot

                            transactions = block.get('transactions', [])
                            if not transactions:
                                print(f"No transactions found for slot {slot}")
                            for tx in transactions:
                                store_transaction(tx, slot, block_number)

                            latest_block = slot
                            break
                        else:
                            print(f"No block data for slot {slot}")
                    except requests.RequestException as e:
                        print(f"Error fetching block {slot}: {e}")


            time.sleep(2)
    except Exception as e:
        print(f"Error while monitoring blocks: {e}")

if __name__ == "__main__":
    monitor_blocks()
    db.close()
