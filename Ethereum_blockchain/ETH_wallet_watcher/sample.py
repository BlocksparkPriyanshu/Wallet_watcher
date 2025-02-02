import csv

# List of addresses
addresses = [
    "0x0ff7E15F615a9d6B1F6A4470651e51138B196185",
    "0x6571e50e8769d236414f3fB9e9B1D05341f6f79a",
    "0x59ac6a6944e078B780d14fE6D92Dcc1CA9257bf0",
    "0x187fE1a8B76c60b85c00A2819152ff00Ff642386",
    "0xb34B53361bd7712888EE4B05A9EE1F7c487921ca"
    
]

# Open the CSV file in write mode
with open('addresses.csv', mode='w', newline='') as file:
    # Create a CSV writer object
    csv_writer = csv.writer(file)
    
    # Write the header
    csv_writer.writerow(['to_address'])
    
    # Write the addresses
    for address in addresses:
        csv_writer.writerow([address])
