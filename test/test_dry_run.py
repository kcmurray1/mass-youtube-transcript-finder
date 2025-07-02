import pytest
from transcriber.transcript import TranscriptProcessor

from transcriber.logger import LocalLogger, DBLogger
from functools import partial

from transcriber.screaper_threaded import ScraperThreaded

from transcriber.scraper import Scraper
from transcriber.scraperworker import ScraperWorker
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling
import queue


# @pytest.fixture(scope='session')
# def transcriber():
#     yield TranscriptProcessor()

# def test_run_with_four_workers(transcriber : TranscriptProcessor):
#     # find videos

#     # search videos
#     homepage_url = 'https://www.youtube.com/@jdh/videos'
#     playlist_url = 'https://www.youtube.com/watch?v=Z9L7u-602qQ&list=PLXVfT_0eTq66k_xLrdBWuZvDe8_UAyK0R'
#     transcriber.channel_search(author='jdh', url=homepage_url, num_workers=4, phrase="hello")


from selenium import webdriver

# def test_new_implementation():
#         def dummy(transcript, phrase):    
#             return "\n".join([match for line in transcript if (match := line.get_dom_attribute("aria-label")) and phrase in match.lower()])

#         url = ''
        
#         main_driver = webdriver.Chrome()
#         videos = Scraper.find_videos(url, author='', driver=main_driver)
#         main_driver.quit()
#         videos = videos[:500]
        
#         dummy_with_phrase = partial(dummy, phrase="")
#         num_workers = 4

#         l = LocalLogger(filepath='matches.txt', error_filepath='error_log.txt',dir='test')

#         ScraperThreaded.get_transcripts(videos=videos, author='', log=l, transcript_op=dummy_with_phrase, num_workers=num_workers)

def test_db_implementation():

    url = 'https://www.youtube.com/@Flarvain/videos'
    
    main_driver = webdriver.Chrome()
    videos = Scraper.find_videos(url, author='flarvain', driver=main_driver)
    main_driver.quit()

    

    num_workers = 4

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
        pool_size=10,
        pool_name="worker_pool",
        **dbconfig

    )
    db = DBLogger(conn_pool)

    ScraperThreaded.get_transcripts(videos=videos, author='', log=db, transcript_op=default_transcript, num_workers=num_workers)
      