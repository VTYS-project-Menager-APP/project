import requests
from bs4 import BeautifulSoup

url = "https://www.investing.com/economic-calendar/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    # "X-Requested-With": "XMLHttpRequest",
    # "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Successfully fetched the page!")
        # print(response.text[:500])
        soup = BeautifulSoup(response.text, 'html.parser')
        # Try to find the calendar table
        table = soup.find('table', {'id': 'economicCalendarData'})
        if table:
            print("Found economicCalendarData table!")
        else:
            print("Table economicCalendarData not found.")
    else:
        print(f"Failed to fetch page. Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
