import os
import requests
import json
from io import BytesIO

APP_ID = os.environ.get("MATHPIX_APP_ID")
APP_KEY = os.environ.get("MATHPIX_APP_KEY")
API_URL = "https://api.mathpix.com/v3/pdf"
CONVERTER_URL = "https://api.mathpix.com/v3/converter"

HEADERS = {
    "Content-Type": "application/json",
    "app_id": APP_ID,
    "app_key": APP_KEY,
}


def send_pdf(pdf_url):
    _data = {
        'url': pdf_url,
        'conversion_formats': {
            'tex.zip': True
        }
    }
    response = requests.post(API_URL, data=json.dumps({'url': pdf_url, 'conversion_formats': {'tex.zip': True}}), headers=HEADERS)
    response_data = response.json()
    if response.status_code != 200 or 'error' in response_data:
        print(f"Algo falló, {response_data}")
        return None

    return response_data.get('pdf_id')


def get_processing_status(job_id):
    response = requests.get(f"{API_URL}/{job_id}", headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed JOB id status retieval: {job_id}")
        return None

    response_data = response.json()

    if 'error' in response_data:
        print(f"Failed JOB id status retieval: {job_id}, details: {response_data}")
        return None

    percent = response_data['percent_done']
    current_status = response_data['status']
    return percent, current_status


def get_conversion_status(job_id):
    response = requests.get(f"{CONVERTER_URL}/{job_id}", headers=HEADERS)
    response_data = response.json()

    if response.status_code != 200 or 'error' in response_data:
        print(f"Failed conversion status retrieval for {job_id}, response: {response_data}")
        return None

    return response_data['status']


def download_latex(job_id):
    response = requests.get(f"{API_URL}/{job_id}.tex", headers=HEADERS)
    data = {}

    try:
        data = response.json()
    except json.decoder.JSONDecodeError:
        pass

    if response.status_code != 200 or 'error' in data:
        print(f"Failed downloading latex for {job_id}. Info: {data}")
        return None

    return BytesIO(response.content)
