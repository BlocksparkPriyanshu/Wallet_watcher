import csv
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from solana.keypair import Keypair

# Number of addresses to generate
num_addresses = 5

csv_file = 'solana_addresses.csv'

# Function to generate and store Solana addresses
def generate_and_store_addresses(num_addresses, csv_file):
    # Generate mnemonic
    mnemo = Mnemonic("english")
    mnemonic = mnemo.generate(strength=128)
    print(f"Mnemonic: {mnemonic}")
    
    # Generate seed from mnemonic
    seed = Bip39SeedGenerator(mnemonic).Generate()
    
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Derivation Path', 'Public Key', 'Private Key', 'Address'])
        if file.tell() == 0:
            writer.writeheader()
        
        for i in range(num_addresses):
            derivation_path = f"m/44'/501'/0'/0/{i+1}"
            bip44_mst_ctx = Bip44.FromSeed(seed, Bip44Coins.SOLANA)
            bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
            
            private_key_bytes = bip44_acc_ctx.PrivateKey().Raw().ToBytes()
            keypair = Keypair.from_secret_key(private_key_bytes)
            
            private_key = private_key_bytes.hex()
            keypair = Keypair()
            address = keypair.public_key.to_base58().decode()
            public_key = keypair.public_key
            
            # Write data to CSV file
            writer.writerow({
                'Derivation Path': derivation_path,
                'Public Key': public_key,
                'Private Key': private_key,
                'Address': address
            })

            # Print the generated Solana account details (optional)
            print(f"Derivation Path: {derivation_path}")
            print(f"Public Key: {public_key}")
            print(f"Private Key: {private_key}")
            print(f"Address: {address}")
            print("---")

# Call the function to generate and store addresses
generate_and_store_addresses(num_addresses, csv_file)

def read_csv_file(csv_file):
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            print(row)

print(f"{num_addresses} Solana addresses generated and stored in {csv_file}.")

