import requests
from bs4 import BeautifulSoup

# URL of the website
url = "https://sih.gov.in/sih2024PS"

# Custom headers to simulate a browser visit
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Make a request to the website with SSL verification disabled
response = requests.get(url, headers=headers, verify=False)

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find the table by its ID
table = soup.find('table', id='dataTablePS')

# Get all rows in the table body
rows = table.find('tbody').find_all('tr')

ps_data = []  # List to store the problem statement data

# Iterate and extract data with exception handling
for row in rows:
    try:
        # Only get the top-level <td> elements, excluding nested tables or modals
        cells = [td for td in row.find_all('td', recursive=False)]

        if len(cells) >= 6:
            ps_number = cells[4].text.strip()
            ideas_count = cells[5].text.strip()

            # Append to the ps_data list
            ps_data.append((ps_number, ideas_count))

            # Print the extracted data
            print(f"PS Number: {ps_number}, Ideas Count: {ideas_count}")
    except Exception as e:
        print(f"Error processing row: {e}")

# Print the length of the array
print(f"Total number of problem statements: {len(ps_data)}")
