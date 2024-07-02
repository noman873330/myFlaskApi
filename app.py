from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
import json
import pandas as pd

app = Flask(__name__)

def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to fetch {url}, status code: {response.status_code}")
        return None

def parse_google_jobs(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    job_results = []

    for result in soup.select('.iFjolb'):
        title = result.select_one('.BjJfJf').get_text(strip=True)
        company = result.select_one('.vNEEBe').get_text(strip=True)

        location_via = result.select('.Qk80Jf')
        location = location_via[0].get_text(strip=True) if location_via else None
        via = location_via[1].get_text(strip=True) if len(location_via) > 1 else None

        thumbnail_elem = result.select_one('.pJ3Uqf img')
        thumbnail = thumbnail_elem['src'] if thumbnail_elem else None

        extensions = [span.get_text(strip=True) for span in result.select('.KKh3md span')]

        job_results.append({
            'title': title,
            'company': company,
            'location': location,
            'via': via,
            'thumbnail': thumbnail,
            'extensions': extensions
        })

    return job_results

@app.route('/scrape-google-jobs', methods=['GET'])
def scrape_google_jobs():
    params = {
        'q': 'San Francisco',
        'ibp': 'htl;jobs',
        'uule': 'w+CAIQICINVW5pdGVkIFN0YXRlcw',
        'hl': 'en',
        'gl': 'us',
    }

    URL = f"https://www.google.com/search?q={params['q']}&ibp={params['ibp']}&uule={params['uule']}&hl={params['hl']}&gl={params['gl']}"
    html_content = fetch_page(URL)

    if html_content:
        job_results = parse_google_jobs(html_content)
        return jsonify(job_results)
    else:
        return jsonify({"error": "Failed to fetch page"})

if __name__ == '__main__':
    app.run(debug=True)
