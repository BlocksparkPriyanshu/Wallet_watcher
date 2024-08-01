import requests
import csv
import mysql.connector
import time

ADDRESSES_CSV_FILE = "/home/ubuntu/Wallet_watcher/Bitcoin_blockchain/addresses.csv"
BLOCKCHAIN_INFO_ADDRESS_URL = "https://blockchain.info/rawblock/"

# Connect to MySQL database
def connect_to_db():
    try:
        db = mysql.connector.connect(
            host="192.168.1.10",
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



def fetch_transaction_details(address):
    try:
        response = requests.get(f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full")
        print(response)
        address_data = response.json()
        print(f"Fetched transactions for address: {address}")
        
        return address_data.get('txs', [])
    except requests.RequestException as e:
        print(f"Error fetching transactions for address {address}: {e}")
        return []

def process_addresses():
    print("Processing addresses from CSV file...")
    try:
        with open(ADDRESSES_CSV_FILE, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            for row in csv_reader:
                if row:
                    to_address = row[0]
                    
                    print(f"Processing to_address: {to_address}")
                    # Assuming fetch_transaction_details function fetches transaction details
                    transactions = fetch_transaction_details(to_address)
                    # print(transactions)
                    for tx in transactions:
                        store_transaction(tx, to_address)
                        print(f"Stored transaction {tx['hash']} for to_address {to_address}")
            print("Finished processing addresses.")
    except FileNotFoundError:
        print(f"File {ADDRESSES_CSV_FILE} not found.")
    except Exception as e:
        print(f"Error processing addresses: {e}")



def store_transaction(tx, to_address):
    global cursor, db
    try:
        if not db.is_connected():
            db = connect_to_db()
            cursor = db.cursor()

        # Set default for from_address
        from_address = None
        block_number = tx.get('block_height')

        # Check if from_address can be extracted
        if 'inputs' in tx:
            for input in tx['inputs']:
                if 'prev_out' in input and 'addr' in input['prev_out']:
                    from_address = input['prev_out']['addr']
                    break

        # If from_address is still None, set it to a default value or placeholder
        if not from_address:
            from_address = "UNKNOWN"

        transaction_hash = tx['hash']
        value= None
        # Ensure 'out' field exists in the transaction
        if 'out' in tx:
            value = next((out['value'] for out in tx['out'] if out.get('addr') == to_address), None)
            if value is not None:
                value /= 100000000  # Convert satoshis to BTC

        sql = """
                INSERT INTO blockchain_db.receive_bitcoin_watcher (from_address, to_address, transaction_hash, block_number, value)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE from_address=VALUES(from_address), to_address=VALUES(to_address), value=VALUES(value), transaction_hash=VALUES(transaction_hash)
                """
        # print("SQL Query:", sql)
        print("Data:", (from_address, to_address, transaction_hash, block_number, value))
        cursor.execute(sql, (from_address, to_address, transaction_hash, block_number, value))
        db.commit()

        print(f"Stored transaction {transaction_hash} with from_address {from_address} and to_address {to_address}")
       
        db = connect_to_db()
        cursor = db.cursor()
    except Exception as e:
        print(f"Error storing transaction: {e}")



# Start processing addresses
if __name__ == "__main__":
    process_addresses()
    db.close()
