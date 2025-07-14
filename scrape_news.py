# PURPOSE: TO SCRAPE NEWS AND ADD IT INTO THE DATABASE FOR THE SPOTIFY-NEWS INTERFACE

import requests
from bs4 import BeautifulSoup
import nlpcloud
import sqlite3 
import dateparser
from tzlocal import get_localzone
from datetime import datetime
from selenium import webdriver
import pandas as pd

con = sqlite3.connect("music_news.db", check_same_thread=False)
cur = con.cursor()

cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_music_news_link ON music_news(link)")
con.commit()

API_KEY = '9c5f3c8a933191b149bb85676f827f651e57a859'
client = nlpcloud.Client("bart-large-cnn", API_KEY)

def string_cleaner(text):
    text = text.replace('\t', '')
    return " ".join(text.replace('\n', '').split())

def convert_to_date(time_string):
    local_tz = get_localzone()

    # Use dateparser to parse both relative and absolute time expressions
    parsed_time = dateparser.parse(
        time_string,
        settings={
            'TIMEZONE': str(local_tz),
            'TO_TIMEZONE': 'UTC',
            'RETURN_AS_TIMEZONE_AWARE': True,
            'PREFER_DAY_OF_MONTH': 'first',
            'RELATIVE_BASE': datetime.now(local_tz),
        }
    )

    if not parsed_time:
        raise ValueError(f"Could not parse time string: '{time_string}'")

    # Format as SQLite timestamp (UTC)
    sqlite_timestamp = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
    return sqlite_timestamp


def getNewsDataFromGoogle():
    headers = {
        'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.google.com/search?q=spotify&gl=us&tbm=nws&num=100")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    data = []

    for el in soup.select("div.SoaBEf"):
        img_tag = el.select_one(".uhHOwf.BYbUcd img")
        img_src = img_tag['src'] if img_tag and 'src' in img_tag.attrs else 'https://upload.wikimedia.org/wikipedia/commons/a/a3/Image-not-found.png'

        data.append((
            convert_to_date(el.select_one(".LfVVr").get_text()), # date
            el.select_one(".NUnG9d span").get_text(), # source
            el.find("a")["href"], # link
            el.select_one(".MBeuO").get_text(), # title
            el.select_one(".GI74Re").get_text(), # description
            img_src
        ))
    
    driver.quit()
    # inserts into database
    try:
        cur.executemany("INSERT OR IGNORE INTO music_news (date, source, link, title, description, news_image) VALUES (?, ?, ?, ?, ?, ?)", data)
        con.commit()
        print(pd.read_sql_query("SELECT date, source, title FROM music_news", con))
    except Exception as e:
        print(e)


def get_description(article_link, headers):
    response = requests.get(article_link, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    article_text = ''

    content_div = soup.select_one('.entry-content .cell.small-12.large-750')
    if content_div:
        for el in content_div.find_all(['p', 'h2']):
            article_text += string_cleaner(el.get_text()) + " "

    try:
        article_date = soup.select_one('p.byline').get_text()
    except:
        article_date = datetime.now()

    try:
        return [article_date, client.summarization(article_text)['summary_text']]
    except Exception as e:
        return [article_date, article_text]



def getNewsDataFromSpotify():
    headers = {
        'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }

    news_results = {
        "news-announcements" : [],
        "trends-data" : [],
        "creator-stories" : [],
        "behind-business" : []
    }

    data = []
    for key in news_results:
        response = requests.get(f"https://newsroom.spotify.com/news/?_filter={key}", headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        for el in soup.select('.grid-item'):
            article_link = el.select_one(".title h3 a")["href"]
            date_and_description = get_description(article_link, headers)

            article_data = (
                string_cleaner(date_and_description[0]), # date,
                f"Spotify Newsroom - {key}", # source
                article_link, # link
                string_cleaner(el.select_one(".title > h3").get_text()), # title
                date_and_description[1], # description
                el.select_one(".post-box .image img")["src"] #image
            )
            data.append(article_data)
        try:
            cur.executemany("INSERT INTO music_news (date, source, link, title, description, news_image) VALUES (?, ?, ?, ?, ?, ?)", data)
            con.commit()
        except Exception as e:
            print(e)


if (len(cur.execute('SELECT * FROM music_news').fetchall()) == 0):
    getNewsDataFromSpotify() 
    getNewsDataFromGoogle()   
#print(pd.read_sql_query("SELECT * FROM music_news", con))
