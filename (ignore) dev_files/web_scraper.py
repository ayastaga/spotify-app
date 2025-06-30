

import itertools
import threading
import time
import sys

done = False
def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rloading ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!     ')


import requests
from bs4 import BeautifulSoup
import nlpcloud
def get_wikipedia_about(name):
    url = f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return ""
    
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.select('p')  # First paragraphs after infobox
    
    for para in paragraphs:
        text = para.get_text().strip()
        if text:  # Skip empty paragraphs
            client = nlpcloud.Client("bart-large-cnn", "378c152ef2478d5db238e96a125c1b01e703220f")
            return client.summarization(wikipedia_text)['summary_text']
    return ""

