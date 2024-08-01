import csv

# List of addresses
addresses = [
    "39B1Dp8y1ynp8fMdBReDAwwKDS1yGUg5Nr",
    "1AR9sWV7ZR2C2ohGSDDKXipCfZ3RLGynHM",
    "bc1qrdfdz7gcup0dvgs0g0ltpxv3saz3mwclpjqnqq",
    "16XRMXef43i98YvfTvvsfMuBa79Z6KCebG",
    "362ziSe1viW7e8hdBguZ3kXojx9ao6h4gu"
    
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
