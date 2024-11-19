import json

import sys

id = sys.argv[1]

# Step 1: Read JSON from two files
with open('data/operator_' +id+'.json', 'r') as file1:
    json1 = json.load(file1)

with open('data/user_' +id+'.json', 'r') as file2:
    json2 = json.load(file2)

# Step 2: Merge the JSON objects
json1["flights"] = json2
merged_json = json1

# Step 3: (Optional) Write the merged data to a new file
with open('data/case_merged'+id+'.json', 'w') as merged_file:
    json.dump(merged_json, merged_file, indent=2)

# Output the merged JSON to the console (optional)
print(json.dumps(merged_json, indent=2))