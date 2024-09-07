from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from flask_caching import Cache
import statistics

app = Flask(__name__)

# Configure cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Configuration
URL = "https://sih.gov.in/sih2024PS"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


@cache.memoize(timeout=3600)  # Cache for 1 hour
def scrape_website():
    response = requests.get(URL, headers=HEADERS, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', id='dataTablePS')
    rows = table.find('tbody').find_all('tr')

    ps_data = {}
    for row in rows:
        try:
            cells = [td for td in row.find_all('td', recursive=False)]
            if len(cells) >= 6:
                ps_number = cells[4].text.strip()
                ideas_count = int(cells[5].text.strip())
                ps_data[ps_number] = ideas_count
        except Exception as e:
            print(f"Error processing row: {e}")

    return ps_data


@app.route('/api/ps-data', methods=['GET'])
def get_ps_data():
    ps_data = scrape_website()
    total_submissions = sum(ps_data.values())
    average_submissions = statistics.mean(ps_data.values()) if ps_data else 0

    return jsonify({
        'ps_data': ps_data,
        'total_submissions': total_submissions,
        'average_submissions': round(average_submissions, 2),
        'problem_statement_count': len(ps_data)
    })


@app.route('/api/ps/<ps_number>', methods=['GET'])
def get_specific_ps(ps_number):
    ps_data = scrape_website()
    if ps_number in ps_data:
        return jsonify({
            'ps_number': ps_number,
            'ideas_count': ps_data[ps_number]
        })
    else:
        return jsonify({'error': 'Problem Statement not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
