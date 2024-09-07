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
table = soup.find("table", {"id": "dataTablePS"})

# Get all rows in the table body
rows = table.find_all("tr", recursive=False)


# Iterate and extract data with exception handling
for row in rows:

    a = row.find_all("td",  recursive=False)[-4:]

    b = row.find_all("td")[:3]

    # print(b)

    print(row)

    # category = a[0]
    # ps_number = a[1]
    # ideas_count = a[2]

    # print(f"S.No.: {s_no}, Organization: {organization}, PS Title: {ps_title}, Category: {
    #       category}, PS Number: {ps_number}, Ideas Count: {ideas_count}")
    # print(f" Category: {
    #     category}, PS Number: {ps_number}              ")
