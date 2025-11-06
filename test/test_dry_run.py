import pytest
# from transcriber.logger import LocalLogger, DBLogger
from functools import partial
# from transcriber.screaper_threaded import ScraperThreaded
from transcript_finder.transcriber.scraper import Scraper
import os
from dotenv import load_dotenv
from mysql.connector import pooling


from selenium import webdriver

# def test_with_local_logger():
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

def test_with_db_logger():

    url = ''
    
    main_driver = webdriver.Chrome()
    videos = Scraper.find_videos(url, author='', driver=main_driver)
    main_driver.quit()

    

    num_workers = 14

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
      