import requests
from pathlib import Path


def download_pictures(filename, url):
    path_to_pictures = Path.cwd()
    response = requests.get(url)
    response.raise_for_status()
    with open(Path() / path_to_pictures / filename, 'wb') as file:
        file.write(response.content)
