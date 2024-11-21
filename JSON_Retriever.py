def get_flight_data(html_file_path):
    with open(html_file_path, 'r') as file:
        html_content = file.read()
    
    # Extract the JSON data from the script tag
    import re
    match = re.search(r'const flightData = (\{.*?\});', html_content, re.DOTALL)
    
    if match:
        import json
        flight_data_str = match.group(1)
        
        # Replace JavaScript object notation with valid JSON
        flight_data_str = flight_data_str.replace("'", '"')
        
        # Parse the JSON string
        return json.loads(flight_data_str)
    else:
        return None

if __name__ == '__main__':
    file_path = '/Users/darshdoshi/Documents/BAIR_Full/UAM_GUI/Userside.html'
    data = get_flight_data(file_path)
    print(data)