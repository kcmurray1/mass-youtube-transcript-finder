import pytest
from selenium import webdriver
from transcriber.scraperworker import ScraperWorker
from transcriber.logger import Logger,  DBLogger
from transcriber.scraper import Scraper
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling
import queue
from functools import partial

# @pytest.fixture(scope='session')
# def driver():
#     test_driver = webdriver.Chrome()
#     yield test_driver

#     test_driver.quit()

# @pytest.fixture(autouse=True)
# def reset_driver_state(driver):
#     # This runs before every test automatically
#     driver.delete_all_cookies()

# def test_work():
#     l = Logger(filepath='goob.txt', error_filepath='goob_error.txt', dir='test')

#     worker = ScraperWorker(id=1, logger=l)
#     url = 'https://www.youtube.com/watch?v=Pi3bI-YghF0'
#     worker.work("jdh", "hello", video_url=url)

def test_write_to_db():
    video_url = 'https://www.youtube.com/watch?v=Pi3bI-YghF0'

    def default_transcript(transcript):
        return "\n".join([line.get_dom_attribute("aria-label") for line in transcript])

    def write_to_db(driver, video_url, db_logger, transcript_op):
        driver.get(video_url)  
        home_channel_url, title, date, uploader = Scraper.get_video_information(driver)
    
 
        # get transcript from url  
        transcript = Scraper.get_transcript(driver, ignore_desc_btn=True)
   
      
        channel_id = db_logger.log_channel(uploader)
    
        video_id = db_logger.log_video(channel_id, video_url, title, date)

        db_logger.log_transcript(video_id, transcript_op(transcript))
  
    load_dotenv()
    dbconfig = {
          'database' : os.getenv('DEV_DB'),
            'user': os.getenv('USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'host' :'localhost'
    }
    conn_pool = pooling.MySQLConnectionPool(
        pool_size=10,
        pool_name="worker_pool",
        **dbconfig

    )
    db = DBLogger(conn_pool)
    worker = ScraperWorker(id=2, logger=db)
    q = queue.Queue()
    q.put(video_url)
    worker.get_transcript_v2(video_queue=q, video_handler=write_to_db, transcript_op=default_transcript)

     
    

   
    
        
