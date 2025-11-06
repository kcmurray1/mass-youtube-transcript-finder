import pytest
import mysql.connector
import os
from selenium import webdriver
from dotenv import load_dotenv
from transcript_finder.transcriber.logger import LocalLogger, DBLogger
"""Tested 11/04/2025"""
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

from transcript_finder.transcriber.scraper import Scraper
from transcript_finder.transcriber.dynamic_page import DynamicPage
from mysql.connector import pooling
def test_log_from_scraper():
    driver = webdriver.Chrome()
    url = ''
    driver.get(url)
    # Get video information from url
    
    home_channel_url, title, date, uploader = Scraper.get_video_information(driver)
    # get transcript from url  
    transcript = DynamicPage.get_transcript(driver, ignore_desc_btn=True)

    assert not isinstance(transcript, Exception)

    def default_transcript(transcript):
        return "\n".join([line.get_dom_attribute("aria-label") for line in transcript])
    load_dotenv()
 
    dbconfig = {
        'database' : os.getenv('DEV_DB'),
        'user': os.getenv('USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'host' :'localhost'
    }
    conn_pool = pooling.MySQLConnectionPool(
        pool_size=32,
        pool_name="worker_pool",
        **dbconfig
    )
    db = DBLogger(conn_pool)
    channel_id = db.log_channel(uploader)
    
    video_id = db.log_video(channel_id, url, title, date)

    db.log_transcript(video_id, default_transcript(transcript))
    

