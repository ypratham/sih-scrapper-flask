import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
URL = "https://sih.gov.in/sih2024PS"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")


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


def send_email(subject, body):
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = RECIPIENT_EMAIL
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(message)


def check_and_notify(ps_number, previous_data):
    current_data = scrape_website()

    if ps_number in current_data:
        current_count = current_data[ps_number]
        previous_count = previous_data.get(ps_number, 0)

        if current_count != previous_count:
            subject = f"Update for PS Number {ps_number}"
            body = f"The ideas count for PS Number {
                ps_number} has changed from {previous_count} to {current_count}."
            send_email(subject, body)
            print(f"Notification sent for PS Number {ps_number}")

        previous_data[ps_number] = current_count
    else:
        print(f"PS Number {ps_number} not found in the current data.")


def main():
    ps_number = input("Enter the PS number you want to track: ")
    interval_hours = int(input("Enter the interval in hours (2 or 4): "))

    if interval_hours not in [2, 4]:
        print("Invalid interval. Defaulting to 2 hours.")
        interval_hours = 2

    previous_data = {}

    def job():
        check_and_notify(ps_number, previous_data)

    schedule.every(interval_hours).hours.do(job)

    print(f"Tracking PS Number {ps_number} every {
          interval_hours} hours. Press Ctrl+C to stop.")

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            print("Tracking stopped.")
            break


if __name__ == "__main__":
    main()
