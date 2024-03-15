import requests
import sys
from urllib.parse import urlparse, parse_qs

def direct_download(url, destination):
    response = requests.get(url, stream=True)
    save_response_content(response, destination)

def download_file_from_google_drive(url, destination):
    # Extract ID from Google Drive URL
    query = urlparse(url).query
    params = parse_qs(query)
    id = params.get('id', [None])[0]

    if id is None:
        print("Google Drive URL is invalid.")
        return

    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # Filter out keep-alive new chunks
                f.write(chunk)

def is_google_drive_url(url):
    netloc = urlparse(url).netloc
    return 'drive.google.com' in netloc or 'docs.google.com' in netloc

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python download.py URL destination")
        sys.exit(1)

    url = sys.argv[1]
    destination = sys.argv[2]

    if is_google_drive_url(url):
        download_file_from_google_drive(url, destination)
    else:
        direct_download(url, destination)
