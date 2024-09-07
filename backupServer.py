from flask import Flask, jsonify, render_template
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
    ps_category_data = {'hardware': [], 'software': []}

    for row in rows:
        try:
            cells = [td for td in row.find_all('td', recursive=False)]

            if len(cells) >= 6:
                ps_category = cells[3].text.strip().lower()
                ps_number = cells[4].text.strip()
                ideas_count = int(cells[5].text.strip())

                ps_data[ps_number] = {
                    'category': ps_category,
                    'ideas_count': ideas_count
                }

                # Collect data for each category
                if ps_category in ps_category_data:
                    ps_category_data[ps_category].append(ideas_count)

        except Exception as e:
            print(f"Error processing row: {e}")

    return ps_data, ps_category_data


@app.route('/dashboard')
def dashboard():
    ps_data, ps_category_data = scrape_website()
    total_submissions = sum([data['ideas_count'] for data in ps_data.values()])
    average_submissions = statistics.mean(
        [data['ideas_count'] for data in ps_data.values()]) if ps_data else 0
    median_submissions = statistics.median(
        [data['ideas_count'] for data in ps_data.values()]) if ps_data else 0
    max_submissions = max([data['ideas_count']
                          for data in ps_data.values()]) if ps_data else 0
    min_submissions = min([data['ideas_count']
                          for data in ps_data.values()]) if ps_data else 0

    # Calculate distribution of submissions
    ranges = [0, 10, 50, 100, 500, float('inf')]
    distribution = [0] * (len(ranges) - 1)
    for data in ps_data.values():
        count = data['ideas_count']
        for i, (lower, upper) in enumerate(zip(ranges, ranges[1:])):
            if lower <= count < upper:
                distribution[i] += 1
                break

    # Category-specific analytics
    category_analytics = {}
    for category in ['hardware', 'software']:
        counts = ps_category_data.get(category, [])
        category_analytics[category] = {
            'total_submissions': sum(counts),
            'average_submissions': round(statistics.mean(counts), 2) if counts else 0,
            'median_submissions': statistics.median(counts) if counts else 0,
            'max_submissions': max(counts) if counts else 0,
            'min_submissions': min(counts) if counts else 0,
            'problem_statement_count': len(counts)
        }

    return render_template('dashboardBackup.html',
                           ps_data=ps_data,
                           total_submissions=total_submissions,
                           average_submissions=round(average_submissions, 2),
                           median_submissions=median_submissions,
                           max_submissions=max_submissions,
                           min_submissions=min_submissions,
                           problem_statement_count=len(ps_data),
                           distribution=distribution,
                           category_analytics=category_analytics)


if __name__ == '__main__':
    app.run(debug=True)
