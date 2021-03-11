import tweepy
import time
import random
import dropbox
import os
from os import environ
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

dbx = dropbox.Dropbox(environ['TOKEN'])

consumer_key=environ['consumer_key']
consumer_secret=environ['consumer_secret']
key=environ['key']
secret=environ['secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
api = tweepy.API(auth)

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_experimental_option("prefs", {"profile.block_third_party_cookies": True})
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--start-maximized')

media_ids = []

file = "last_seen.txt"
file_location = f"/LastSeen/{file}"

def read_file(dbx, file):
    _, f = dbx.files_download(file)
    f = f.content
    f = f.decode("utf-8")
    return f

def upload_file(dbx, file_location, file):
    with open(file, "rb") as f:
        dbx.files_upload(f.read(),file_location,mode=dropbox.files.WriteMode.overwrite)

def store_last_seen(FILE_NAME,last_seen_id):
    file_write = open(file,'w')
    file_write.write(str(last_seen_id))
    file_write.close()
    return

def reply():
    tweets = api.mentions_timeline(read_file(dbx, file_location),tweet_mode='extended')
    for tweet in reversed(tweets):
        url = get_url(tweet)
        if url != "":
            driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
            driver.get(url)

            S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
            driver.set_window_size(S('Width'),S('Height')/1.5)
            driver.find_element_by_tag_name('body').screenshot('screenshot.png')

            
            driver.quit()

            media = api.media_upload('screenshot.png')
            media_ids.append(media.media_id)
            api.update_status('@'+tweet.user.screen_name, tweet.id, media_ids=media_ids)
            os.remove('screenshot.png')
            media_ids.clear()

            store_last_seen(file,tweet.id)
            upload_file(dbx, file_location, file)

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
    except:
        time.sleep(15)
        continue
    time.sleep(15)