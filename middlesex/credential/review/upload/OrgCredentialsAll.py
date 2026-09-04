import os
import requests
import csv
import json

# Define the API URL
url = 'https://apps.credentialengine.org/assistant/search/ctdl'  # Replace with the actual endpoint

# Read the API token from the environment instead of hardcoding it.
# Set it before running, e.g.: export CE_ASSISTANT_API_TOKEN=your-token-here
API_TOKEN = os.environ["CE_ASSISTANT_API_TOKEN"]

# Function to send POST requests and get data
def fetch_data(skip, take=100):
    query_payload = {
        "Query": {
	"@type": {
		"search:value": "ceterms:Credential",
		"search:matchType": "search:subClassOf"
	},
	"ceterms:ownedBy": [
		{
			"ceterms:ctid": "ce-44c3a1b6-fb1f-4430-b6bf-e71a011a590b"
		}
	]
},
        "Skip": skip,
        "Take": take
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_TOKEN}'
    }
    
    # Send the POST request
    response = requests.post(url, headers=headers, data=json.dumps(query_payload))
    
    # Check for a successful response
    if response.status_code == 200:
        return response.json()  # Return the JSON response as a Python dict
    else:
        print(f"Error: Received status code {response.status_code}")
        return None

# Function to save the data in a CSV file
def save_to_csv(data, csv_filename):
    # Open the CSV file for writing
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write the header
        writer.writerow([
            "ID", "Type", "CTID", "Name", "Owned By", "Requires - Name", "Requires - Asserted By",
            "Requires - Credit Value", "Requires - Credit Description", "Description", "Subject Webpage", "TargetNode", "TargetNodeName"
        ])
        
        # Write each record to the CSV file
        for item in data:
            writer.writerow([
                item.get("@id", ""),
                item.get("@type", ""),
                item.get("ceterms:ctid", ""),
                item.get("ceterms:name", {}).get("en-US", ""),
                '|'.join(item.get("ceterms:ownedBy", [])),
                item.get("ceterms:requires", [{}])[0].get("ceterms:name", {}).get("en-US", ""),
                '|'.join(item.get("ceterms:requires", [{}])[0].get("ceterms:assertedBy", [])),
                item.get("ceterms:requires", [{}])[0].get("ceterms:creditValue", [{}])[0].get("schema:value", ""),
                item.get("ceterms:requires", [{}])[0].get("ceterms:creditValue", [{}])[0].get("schema:description", {}).get("en-US", ""),
                item.get("ceterms:description", {}).get("en-US", ""),
                item.get("ceterms:subjectWebpage", ""),
                item.get("ceterms:credentialStatusType", {}).get("ceterms:targetNode", ""),
                item.get("ceterms:credentialStatusType", {}).get("ceterms:targetNodeName", "")
            ])

# Main script logic
def main():
    all_data = []  # List to hold all records
    skip = 0
    take = 100

    while True:
        # Fetch a batch of data
        print(f"Fetching data, skip={skip}")
        response_data = fetch_data(skip, take)

        # Check if we received data
        if response_data and "data" in response_data:
            batch_data = response_data["data"]
            
            # If no more data, break the loop
            if not batch_data:
                break
            
            # Append the batch data to the master list
            all_data.extend(batch_data)

            # Increase the skip value for the next batch
            skip += take
        else:
            break
    
    # Save all collected data to a CSV file
    csv_filename = 'MiddlesexAll.csv'
    save_to_csv(all_data, csv_filename)
    print(f"Data saved to {csv_filename}")

if __name__ == "__main__":
    main()
