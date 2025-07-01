import pytest
 
import os
from selenium import webdriver
from dotenv import load_dotenv
from transcriber.logger import LocalLogger, DBLogger
from transcriber.youtube_element_utils import YtElementUtils

def test_local_logger():
    l = LocalLogger('test_file.txt', 'test_err_file.txt', 'test')

    l.log("Hello world")
    l.log_err("this is an error")

def test_db_logger():
    load_dotenv()
    conn = mysql.connector.connect(
        database=os.getenv('DEV_DB'),
        user=os.getenv('USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host='localhost'
    )
    cursor = conn.cursor()

    cursor.execute("SHOW TABLES")

    print(cursor.fetchall())
    conn.close()

from transcriber.scraper import Scraper

def test_log_from_scraper():
    driver = webdriver.Chrome()
    url = 'https://www.youtube.com/watch?v=WZ3h-9ht_1c'
    driver.get(url)
    # Get video information from url
    
    home_channel_url, title, date, uploader = YtElementUtils.get_video_information(driver)
    # get transcript from url  
    transcript = Scraper.get_transcript(driver, ignore_desc_btn=True)

    assert not isinstance(transcript, Exception)

    def default_transcript(transcript):
        return "\n".join([line.get_dom_attribute("aria-label") for line in transcript])
    load_dotenv()
    conn = mysql.connector.connect(
        database=os.getenv('DEV_DB'),
        user=os.getenv('USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host='localhost'
    )
    db = DBLogger(conn)
    channel_id = db.log_channel(uploader)
    
    video_id = db.log_video(channel_id, url, title, date)

    db.log_transcript(video_id, default_transcript(transcript))
    conn.close()
    

    # log into database

# def test_insert_db():
#     load_dotenv()
#     conn = mysql.connector.connect(
#         database=os.getenv('DEV_DB'),
#         user=os.getenv('USER'),
#         password=os.getenv('MYSQL_PASSWORD'),
#         host='localhost'
#     )
#     # cursor = conn.cursor()
#     # channel_name = 'heepl'
#     # cursor.execute(f"INSERT INTO transcript_finder_app_channel(name) VALUES ('{channel_name}')")
#     url, title, date, owner = ('www.google.com', 'my title is [here]', '2025-05-06', 'beeple')
#     l = DBLogger(conn)

#     channel_id = l.log_channel(owner)
#     l.log_video(channel_id[0], url, title)
#     # conn.commit()
    
#     conn.close()


