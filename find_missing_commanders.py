import json

def read_commander_names(filename):
    with open(filename, 'r') as file:
        return [line.strip().strip('-') for line in file if line.strip()]

def load_json_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def find_missing_commanders(txt_commanders, json_data):
    json_commander_names = set(card['name'] for card in json_data)
    txt_commander_set = set(txt_commanders)
    return txt_commander_set - json_commander_names

def write_missing_commanders(missing_commanders, filename):
    with open(filename, 'w') as file:
        for commander in sorted(missing_commanders):
            file.write(f"{commander}\n")

# Main execution
txt_filename = 'commander_names.txt'
json_filename = 'commanders.json'
output_filename = 'missing_commanders.txt'

# Read commander names from text file
txt_commanders = read_commander_names(txt_filename)

# Load JSON data
json_data = load_json_data(json_filename)

# Find missing commanders
missing_commanders = find_missing_commanders(txt_commanders, json_data)

# Write missing commanders to file
write_missing_commanders(missing_commanders, output_filename)

print(f"Found {len(missing_commanders)} missing commanders.")
print(f"Missing commanders have been written to {output_filename}")