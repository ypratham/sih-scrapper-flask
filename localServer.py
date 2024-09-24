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

    ps_data = {"Hardware": {}, "Software": {}}
    for row in rows:
        try:
            cells = [td for td in row.find_all('td', recursive=False)]

            # print(cells)

            if len(cells) >= 6:
                ps_category = cells[3].text.strip()
                ps_number = cells[4].text.strip()
                ideas_count = int(cells[5].text.strip())
                ps_data[ps_category][ps_number] = ideas_count
        except Exception as e:
            print(f"Error processing row: {e}")

    return ps_data


@app.route('/')
def dashboard():
    ps_data = scrape_website()
    total_submissions = sum(sum(category.values())
                            for category in ps_data.values())
    average_submissions = statistics.mean(
        sum(category.values()) for category in ps_data.values()) if ps_data else 0
    median_submissions = statistics.median(
        sum(category.values()) for category in ps_data.values()) if ps_data else 0
    max_submissions = max(sum(category.values())
                          for category in ps_data.values()) if ps_data else 0
    min_submissions = min(sum(category.values())
                          for category in ps_data.values()) if ps_data else 0

    # Calculate distribution of submissions
    ranges = [0, 10, 50, 100, 500, float('inf')]
    distribution = [0] * (len(ranges) - 1)
    for category in ps_data.values():
        for count in category.values():
            for i, (lower, upper) in enumerate(zip(ranges, ranges[1:])):
                if lower <= count < upper:
                    distribution[i] += 1
                    break

    # Category-specific analytics
    hardware_submissions = sum(ps_data['Hardware'].values())
    software_submissions = sum(ps_data['Software'].values())

    # Calculate averages for each category
    hardware_average = statistics.mean(
        ps_data['Hardware'].values()) if ps_data['Hardware'] else 0
    software_average = statistics.mean(
        ps_data['Software'].values()) if ps_data['Software'] else 0

    # Calculate medians for each category
    hardware_median = statistics.median(
        ps_data['Hardware'].values()) if ps_data['Hardware'] else 0
    software_median = statistics.median(
        ps_data['Software'].values()) if ps_data['Software'] else 0

    # Calculate maximums for each category
    hardware_max = max(ps_data['Hardware'].values()
                       ) if ps_data['Hardware'] else 0
    software_max = max(ps_data['Software'].values()
                       ) if ps_data['Software'] else 0

    # Calculate minimums for each category
    hardware_min = min(ps_data['Hardware'].values()
                       ) if ps_data['Hardware'] else 0
    software_min = min(ps_data['Software'].values()
                       ) if ps_data['Software'] else 0

    return render_template('dashboardBackup.html',
                           ps_data=ps_data,
                           total_submissions=total_submissions,
                           average_submissions=round(average_submissions, 2),
                           median_submissions=median_submissions,
                           max_submissions=max_submissions,
                           min_submissions=min_submissions,
                           problem_statement_count=len(
                               ps_data['Hardware']) + len(ps_data['Software']),
                           distribution=distribution,
                           hardware_submissions=hardware_submissions,
                           software_submissions=software_submissions,
                           hardware_average=round(hardware_average, 2),
                           software_average=round(software_average, 2),
                           hardware_median=hardware_median,
                           software_median=software_median,
                           hardware_max=hardware_max,
                           software_max=software_max,
                           hardware_min=hardware_min,
                           software_min=software_min
                           )

if __name__ == '__main__':
    app.run()

