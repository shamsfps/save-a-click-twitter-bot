import tweepy
import time
import random
import os
from os import environ
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

consumer_key=environ['consumer_key']
consumer_secret=environ['consumer_secret']
key=environ['key']
secret=environ['secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
api = tweepy.API(auth)

FILE_NAME = 'last_seen.txt'

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

media_ids = []

def read_last_seen(FILE_NAME):
    file_read = open(FILE_NAME, 'r')
    last_seen_id = int(file_read.read().strip())
    file_read.close()
    return last_seen_id

def store_last_seen(FILE_NAME,last_seen_id):
    file_write = open(FILE_NAME,'w')
    file_write.write(str(last_seen_id))
    file_write.close()
    return

def reply():
    tweets = api.mentions_timeline(read_last_seen(FILE_NAME),tweet_mode='extended')
    for tweet in reversed(tweets):
        url = get_url(tweet)
        if url != "":
            driver.get(url)
            S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
            driver.set_window_size(S('Width'),S('Height')-(S('Height')*0.4)) # May need manual adjustment
            driver.find_element_by_tag_name('body').screenshot('screenshot.png')
            driver.quit()

            media = api.media_upload('screenshot.png')
            media_ids.append(media.media_id)
            api.update_status('@'+tweet.user.screen_name, tweet.id, media_ids=media_ids)
            store_last_seen(FILE_NAME,tweet.id)
            os.remove('screenshot.png')
            media_ids.clear()

def get_url(tweet):
    if tweet.in_reply_to_status_id is None:
        return ""
    else:
        reply = api.get_status(tweet.in_reply_to_status_id, tweet_mode="extended")
        urls = reply.entities['urls']
        if len(urls) == 0:
            return ""
        else:
            url = urls[0]['expanded_url']
            return url

while True:
    try:
        reply()
    except tweepy.TweepError:
        time.sleep(15)
        continue
    except:
        time.sleep(15)
        continue
    time.sleep(15)